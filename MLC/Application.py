import matlab.engine
import MLC.Log.log as lg

from MLC.Common.PreevaluationManager import PreevaluationManager
from MLC.Log.log import set_logger
from MLC.matlab_engine import MatlabEngine
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.mlc_table.MLCTable import MLCTable
from MLC.Population.Population import Population
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.Scripts.Evaluation.toy_problem import toy_problem
from MLC.Scripts.Evaluation.arduino import arduino
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
        if ngen <= 0:
            lg.logger_.error('The amounts of generations must be a '
                             'positive decimal number. Value provided: '
                             + ngen)
            return

        # The first generation it's a special case, since it must
        # be generated from scratch
        if Population.get_current_pop_number() == 0:
            # population is empty, we have to create it
            self.generate_population()

        # Keep on generating new population while the cut condition is not fulfilled
        while Population.get_current_pop_number() <= ngen:
            current_pop = self._pop_container[Population.get_current_pop_number()]

            # state = self._eng.get_population_state(self._mlc, Population.get_current_pop_number())
            state = current_pop.get_state()

            if state == 'init':
                if Population.get_current_pop_number() == 1:
                    self.generate_population()
                else:
                    self.evolve_population()
            elif state == 'created':
                self.evaluate_population()
            elif state == 'evaluated':
                if fig > 0:
                    self._eng.show_best(self._mlc)

                # if (fig > 1):
                #    self.eng.show_convergence(self.mlc)

                if Population.get_current_pop_number() <= ngen:
                    self.evolve_population()

    def generate_population(self):
        """
        Initializes the population. (MLC2 Toolbox)
        OBJ.GENERATE_POPULATION updates the OBJ MLC2 object with an initial
        population
        The function creates a MLCpop object defining the population and
        launch its creation method according to the OBJ.PARAMETERS content.
        The creation algorithm is implemented in the MLCpop class.
        """

        # REMOVE: Create the MATLAB Population
        population = self._eng.MLCpop(self._config.get_matlab_object())
        self._eng.workspace["wpopulation"] = population

        # Create it's equivalent in Python
        Population.inc_pop_number()
        py_pop = Population()
        self._pop_container[Population.get_current_pop_number()] = py_pop

        # Create the first population
        py_pop.create()

        # Table created inside population create
        # FIXME: It is okay to create the table here?
        # self._eng.set_table(self._mlc, MLCTable.get_instance().get_matlab_object())

        # matlab_array = matlab.double(py_pop.get_individuals().tolist())
        # self._eng.set_individuals(population, matlab_array, nargout=0)

        py_pop.set_state("created")
        # self._eng.set_state(population, 'created')
        lg.logger_.debug('[EV_POP] ' + py_pop.get_state())

        # self._eng.add_population(self._mlc, population, Population.get_current_pop_number())

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
        # self._set_pop_individuals()

        # Enforce reevaluation
        if self._config.getboolean('EVALUATOR', 'ev_again_best'):
            ev_again_times = self._config.getint('EVALUATOR', 'ev_again_times')
            for i in range(1, ev_again_times):
                ev_again_nb = self._config.getint('EVALUATOR', 'ev_again_nb')
                current_pop.evaluate()

                # self._set_pop_individuals()
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
        n = Population.generations()
        table = self._eng.eval('wmlc.table')
        current_pop = Population.population(n)
        next_pop = Population.evolve(current_pop, self._config, table)

        # Increase both counters. MATLAB and Python pops counters
        n += 1
        Population.inc_pop_number()
        self._eng.add_population(self._eng.eval('wmlc'), next_pop, n)

        # Remove duplicates
        look_for_dup = self._config.getboolean('OPTIMIZATION', 'lookforduplicates')

        if look_for_dup:
            self._eng.remove_duplicates(next_pop)
            indivs = Population.get_gen_individuals(n)

            nulls = []
            for idx in xrange(len(indivs[0])):
                if indivs[0][idx] == -1:
                    nulls.append(idx + 1)

            while len(nulls):
                next_pop = Population.evolve(current_pop, self._config, table, next_pop)
                self._eng.remove_duplicates(next_pop)
                indivs = Population.get_gen_individuals(n)

                nulls = []
                for idx in xrange(len(indivs[0])):
                    if indivs[0][idx] == -1:
                        nulls.append(idx + 1)

            self._eng.set_state(next_pop, 'created')
            self._set_pop_new_individuals()

    def _set_pop_new_individuals(self):
        # Create a new population with the indexes updated
        self._pop = Population(self._config,
                               Population.get_current_pop_number())
        self._set_pop_individuals()

    def _set_pop_individuals(self):
        gen_number = Population.get_current_pop_number()
        indivs = Population.get_gen_individuals(gen_number)
        self._pop.set_individuals(
            [(x, indivs[0][x]) for x in xrange(len(indivs[0]))])

    def _set_ev_callbacks(self):
        # Set the callbacks to be called at the moment of the evaluation
        # FIXME: To this dynamically searching .pys in the directory
        EvaluatorFactory.set_ev_callback('toy_problem', toy_problem)
        EvaluatorFactory.set_ev_callback('arduino', arduino)

    def _set_preev_callbacks(self):
        # Set the callbacks to be called at the moment of the preevaluation
        # FIXME: To this dynamically searching .pys in the directory
        PreevaluationManager.set_callback('default', default)
