import matlab.engine
import MLC.Log.log as lg

from MLC.Common.PreevaluationManager import PreevaluationManager
from MLC.Log.log import set_logger
from MLC.matlab_engine import MatlabEngine
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.mlc_table.MLCTable import MLCTable
from MLC.Population.Population import Population
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.Scripts.Evaluation import toy_problem
from MLC.Scripts.Evaluation import arduino
from MLC.Scripts.Preevaluation.default import default


class Application(object):

    def __init__(self, log_mode='console'):
        self._eng = MatlabEngine.engine()
        self._config = Config.get_instance()
        self._set_ev_callbacks()
        self._set_preev_callbacks()

        # Set logger mode of the App
        set_logger(log_mode)

        self._mlc = self._eng.eval('wmlc')
        self._pop_container = {}

    def go(self, ngen, fig):
        """
        Start MLC2 problem solving (MLC2 Toolbox)
            OBJ.GO(N) creates (if necessary) the population, evaluate and
                evolve it until N evaluated generations are obtained.
            OBJ.GO(N,1) additionaly displays the best individual if implemented
                in the evaluation function at the end of each generation
                evaluation
            OBJ.GO(N,2) additionaly displays the convergence graph at the end
                of each generation evaluation
        """
        # Enables/Disable graph of the best individual of every iteration
        show_all_bests = self._config.getboolean('BEHAVIOUR', 'showeveryitbest')
        if ngen <= 0:
            lg.logger_.error('The amounts of generations must be a '
                             'positive decimal number. Value provided: '
                             + ngen)
            return

        # The first generation it's a special case, since it must
        # be generated from scratch
        if Population.get_current_pop_number() == 0:
            self.generate_population()

        # Keep on generating new population while the cut condition is not fulfilled
        while Population.get_current_pop_number() < ngen:
            current_pop = self._pop_container[Population.get_current_pop_number()]
            state = current_pop.get_state()
            if state == 'init':
                if Population.get_current_pop_number() == 1:
                    self.generate_population()
                else:
                    self.evolve_population()
            elif state == 'created':
                self.evaluate_population()
            elif state == 'evaluated':
                if (Population.get_current_pop_number() >= ngen or show_all_bests) and fig > 0:
                    self.show_best()
                # if (fig > 1):
                #    self.eng.show_convergence(self.mlc)

                if Population.get_current_pop_number() < ngen:
                    self.evolve_population()

        # Evaluate the last population
        self.evaluate_population()
        self.show_best()

    def get_population(self, number):
        return self._pop_container[number]

    def generate_population(self):
        """
        Initializes the population. (MLC2 Toolbox)
        OBJ.GENERATE_POPULATION updates the OBJ MLC2 object with an initial
        population
        The function creates a MLCpop object defining the population and
        launch its creation method according to the OBJ.PARAMETERS content.
        The creation algorithm is implemented in the MLCpop class.
        """
        py_pop = Population()
        self._pop_container[Population.get_current_pop_number()] = py_pop

        # Create the first population
        py_pop.create()
        py_pop.set_state("created")
        lg.logger_.debug('[APPLICATION] First population state' + py_pop.get_state())

    def evaluate_population(self):
        """
        Evolves the population. (MLC2 Toolbox)
        OBJ.EVALUATE_POPULATION launches the evaluation method,
        and updates the MLC2 object.
        The evaluation algorithm is implemented in the MLCpop class.
        """
        # First evaluation
        # pop_index = Population.generations()
        # actual_pop = Population.population(pop_index)
        # self._pop.evaluate(range(1, len(self._pop.get_individuals()) + 1))
        current_pop = self._pop_container[Population.get_current_pop_number()]
        current_pop.evaluate()

        # Remove bad individuals
        elim = False
        bad_values = self._config.get('EVALUATOR', 'badvalues_elim')
        if bad_values == 'all':
            elim = True
        elif bad_values == 'first':
            if Population.get_current_pop_number() == 1:
                elim = True

        if elim:
            ret = current_pop.remove_bad_individuals()
            while ret:
                # There are bad individuals, recreate the population
                current_pop.create()
                current_pop.evaluate()
                ret = current_pop.remove_bad_individuals()

        current_pop.sort()

        # Enforce reevaluation
        if self._config.getboolean('EVALUATOR', 'ev_again_best'):
            ev_again_times = self._config.getint('EVALUATOR', 'ev_again_times')
            for i in range(1, ev_again_times):
                ev_again_nb = self._config.getint('EVALUATOR', 'ev_again_nb')
                current_pop.evaluate()
                current_pop.sort()

        current_pop.set_state('evaluated')

    def evolve_population(self):
        """
        Evolves the population. (MLC2 Toolbox)
        OBJ.EVOLVE_POPULATION updates the OBJ MLC2 object with a new MLCpop
        object in the OBJ.POPULATION array
        containing the evolved population
        The evolution algorithm is implemented in the MLCpop class.
        """

        # Evolve the current population and add it to the MLC MATLAB object
        current_pop = self._pop_container[Population.get_current_pop_number()]
        next_pop = current_pop.evolve()

        # Remove duplicates
        look_for_dup = self._config.getboolean('OPTIMIZATION', 'lookforduplicates')

        if look_for_dup:
            # Remove the duplicates in the last evolve
            while next_pop.remove_duplicates() > 0:
                next_pop = current_pop.evolve(next_pop)

        next_pop.set_state("created")
        self._pop_container[Population.get_current_pop_number()] = next_pop

    def show_best(self):
        # Get the best
        best_index = self._pop_container[Population.get_current_pop_number()].get_best_index()
        best_indiv = self._pop_container[Population.get_current_pop_number()].get_best_individual()
        lg.logger_.info("[APPLICATION] Proceed to show the best individual found.")
        lg.logger_.debug("[APPLICATION] Individual N#{0} - Cost: {1}".format(best_index, best_indiv.get_cost()))

        stop_no_graph = self._config.getboolean('BEHAVIOUR', 'stopongraph')
        EvaluatorFactory.get_ev_callback().show_best(best_index, best_indiv, stop_no_graph)

    def _set_ev_callbacks(self):
        # Set the callbacks to be called at the moment of the evaluation
        # FIXME: Dinamically get instances from "MLC.Scripts import *"
        EvaluatorFactory.set_ev_callback('toy_problem', toy_problem)
        EvaluatorFactory.set_ev_callback('arduino', arduino.cost)

    def _set_preev_callbacks(self):
        # Set the callbacks to be called at the moment of the preevaluation
        # FIXME: To this dynamically searching .pys in the directory
        PreevaluationManager.set_callback('default', default)
