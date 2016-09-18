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

class Simulation:
    def __init__(self):
        self._generations = []

    def get_generation(self, gen):
        if gen > len(self._generations):
            raise IndexError("Generation %s do not exist" % gen)
        return self._generations[gen-1]

    def generations(self):
        return len(self._generations)

    def get_last_generation(self):
        if len(self._generations) == 0:
            raise IndexError("Empty simulation")
        return self._generations[self.generations()-1]

    def new_generation(self, population):
        self._generations.append(population)
        return len(self._generations)

class Application(object):

    def __init__(self, log_mode='console'):
        self._eng = MatlabEngine.engine()
        self._config = Config.get_instance()
        self._set_ev_callbacks()
        self._set_preev_callbacks()

        # Set logger mode of the App
        set_logger(log_mode)
        self._simulation = Simulation()

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
        if ngen <= 0:
            raise Exception("Amounts of generations must be a positive number, provided: %s" % ngen)

        show_all_bests = self._config.getboolean('BEHAVIOUR', 'showeveryitbest')

        # First generation must be generated from scratch
        if self._simulation.generations() == 0:
            first_population = Population(1)
            first_population.create()
            first_population.set_state("created")
            self._simulation.new_generation(first_population)
            lg.logger_.debug('First population created')

        # Keep on generating new population while the cut condition is not fulfilled
        while self._simulation.generations() < ngen:
            current_population = self._simulation.get_last_generation()
            state = current_population.get_state()
            if state == 'created':
                self.evaluate_population(current_population)

            elif state == 'evaluated':
                if (self._simulation.generations() >= ngen or show_all_bests) and fig > 0:
                    self.show_best()
                # if (fig > 1):
                #    self.eng.show_convergence(self.mlc)

                if self._simulation.generations() < ngen:
                    next_population = self.evolve_population(current_population)
                    self._simulation.new_generation(next_population)

        # Evaluate the last population
        self.evaluate_population(self._simulation.get_last_generation())
        self.show_best(self._simulation.get_last_generation())

    def get_simulation(self):
        return self._simulation

    def get_population(self, number):
        return self._pop_container[number]

    def evaluate_population(self, population):
        """
        Evolves the population. (MLC2 Toolbox)
        OBJ.EVALUATE_POPULATION launches the evaluation method,
        and updates the MLC2 object.
        The evaluation algorithm is implemented in the MLCpop class.
        """
        # First evaluation
        population.evaluate()

        # Remove bad individuals
        elim = False
        bad_values = self._config.get('EVALUATOR', 'badvalues_elim')
        if bad_values == 'all':
            elim = True
        elif bad_values == 'first':
            if self._simulation.generations() == 1:
                elim = True

        if elim:
            ret = population.remove_bad_individuals()
            while ret:
                # There are bad individuals, recreate the population
                population.create()
                population.evaluate()
                ret = population.remove_bad_individuals()

        population.sort()

        # Enforce reevaluation
        if self._config.getboolean('EVALUATOR', 'ev_again_best'):
            ev_again_times = self._config.getint('EVALUATOR', 'ev_again_times')
            for i in range(1, ev_again_times):
                ev_again_nb = self._config.getint('EVALUATOR', 'ev_again_nb')
                population.evaluate()
                population.sort()

        population.set_state('evaluated')

    def evolve_population(self, population):
        """
        Evolves the population. (MLC2 Toolbox)
        OBJ.EVOLVE_POPULATION updates the OBJ MLC2 object with a new MLCpop
        object in the OBJ.POPULATION array
        containing the evolved population
        The evolution algorithm is implemented in the MLCpop class.
        """

        # Evolve population and add it to the MLC MATLAB object
        next_pop = population.evolve()

        # Remove duplicates
        if self._config.getboolean('OPTIMIZATION', 'lookforduplicates'):
            # Remove the duplicates in the last evolve
            while next_pop.remove_duplicates() > 0:
                next_pop = population.evolve(next_pop)

        next_pop.set_state("created")
        return next_pop

    def show_best(self, population):
        # Get the best
        best_index = population.get_best_index()
        best_indiv = population.get_best_individual()
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
