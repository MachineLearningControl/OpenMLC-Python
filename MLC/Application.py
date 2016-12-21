import MLC.Log.log as lg

from MLC.Common.PreevaluationManager import PreevaluationManager
from MLC.db.mlc_repository import MLCRepository
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.mlc_table.MLCTable import MLCTable
from MLC.Population.Creation.CreationFactory import CreationFactory
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.Population.Population import Population
from MLC.Simulation import Simulation


class MLC_CALLBACKS:
    ON_START = 0
    ON_EVALUATE = 1
    ON_NEW_GENERATION = 2
    ON_FINISH = 3

    @staticmethod
    def pass_callback(*args, **kwargs):
        pass


class Application(object):
    def __init__(self, simulation, log_mode='console', callbacks={}):
        self._config = Config.get_instance()
        # Set logger mode of the App
        set_logger(log_mode)

        self._simulation = simulation
        self._project_validations()

        # bad values and duplicates
        self.__badvalues_elim = self._config.get('EVALUATOR', 'badvalues_elim')

        # Gen creator
        gen_method = self._config.get('GP', 'generation_method')
        self._gen_creator = CreationFactory.make(gen_method)

        # callbacks configuration
        self.__callbacks_manager = MLCCallbacksManager()

        # Gen evaluator
        ev_method = self._config.get('EVALUATOR', 'evaluation_method')
        on_evaluate_callback = callbacks.get(MLC_CALLBACKS.ON_EVALUATE,
                                             MLC_CALLBACKS.pass_callback)

        self._evaluator = EvaluatorFactory.make(ev_method, on_evaluate_callback)

        self._show_all_bests = self._config.getboolean('BEHAVIOUR', 'showeveryitbest')
        self._look_for_duplicates = self._config.getboolean('OPTIMIZATION', 'lookforduplicates')

        # callbacks for the MLC application
        if MLC_CALLBACKS.ON_START in callbacks:
            self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_START,
                                               callbacks[MLC_CALLBACKS.ON_START])

        if MLC_CALLBACKS.ON_NEW_GENERATION in callbacks:
            self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_NEW_GENERATION,
                                               callbacks[MLC_CALLBACKS.ON_NEW_GENERATION])

        if MLC_CALLBACKS.ON_FINISH in callbacks:
            self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_FINISH,
                                               callbacks[MLC_CALLBACKS.ON_FINISH])

    def go(self, to_generation, fig, from_generation=None):
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
        if from_generation is None:
            from_generation = self._simulation.number_of_generations()

        if to_generation <= 0:
            raise Exception("Amounts of generations must be a positive number, provided: %s" % to_generation)

        # valid_from_generation = range(1, min(to_generation, self._simulation.number_of_generations()+1))
        # if not from_generation in valid_from_generation:
        #    raise Exception("from_generation must be a positive number from %s, provided: %s" % (valid_from_generation, from_generation))

        # self._simulation.erase_generations(from_generation+1)

        self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_START)

        # First generation must be generated from scratch
        if self._simulation.number_of_generations() == 0:
            first_population = Simulation.create_empty_population_for(generation=1)
            self._simulation.add_generation(first_population)

        while self._simulation.number_of_generations() < to_generation:
            current_population = self._simulation.get_last_generation()
            current_generation_number = self._simulation.number_of_generations()

            # create
            if not current_population.is_complete():
                current_population.fill(self._gen_creator)

            # evaluate
            self.evaluate_population(current_population, current_generation_number)

            # new generation callback
            self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_NEW_GENERATION,
                                              current_generation_number)

            # show best if necessary
            if (self._simulation.number_of_generations() >= to_generation or self._show_all_bests) and fig:
                self.show_best(self._simulation.get_last_generation())

            # evolve
            next_population = current_population.evolve()
            if self._look_for_duplicates:
                while next_population.remove_duplicates() > 0:
                    next_population = current_population.evolve(next_population)

            # save new generation
            self._simulation.add_generation(next_population)
            MLCTable.get_instance().commit_changes()

        # Evaluate last population
        self.evaluate_population(self._simulation.get_last_generation(),
                                 self._simulation.number_of_generations())

        # new generation callback
        self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_NEW_GENERATION,
                                          self._simulation.number_of_generations())

        if fig:
            self.show_best(self._simulation.get_last_generation())
        MLCTable.get_instance().commit_changes()

        for i in range(from_generation + 1, self._simulation.number_of_generations() + 1):
            p = self._simulation.get_generation(i)
            MLCRepository.get_instance().add_population(p)

        self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_FINISH)

    def get_simulation(self):
        return self._simulation

    def get_population(self, number):
        return self._pop_container[number]

    def evaluate_population(self, population, generation_number):
        """
        Evolves the population. (MLC2 Toolbox)
        OBJ.EVALUATE_POPULATION launches the evaluation method,
        and updates the MLC2 object.
        The evaluation algorithm is implemented in the MLCpop class.
        """
        # First evaluation
        population.evaluate(self._evaluator)

        # Remove bad individuals
        if self._duplicates_must_be_removed(generation_number):
            while population.remove_bad_individuals():
                # There are bad individuals, recreate the population
                population.fill(self._gen_creator)
                population.evaluate(self._evaluator)

        population.sort()

        # Enforce reevaluation
        if self._config.getboolean('EVALUATOR', 'ev_again_best'):
            ev_again_times = self._config.getint('EVALUATOR', 'ev_again_times')
            for i in range(1, ev_again_times):
                ev_again_nb = self._config.getint('EVALUATOR', 'ev_again_nb')
                population.evaluate(self._evaluator)
                population.sort()

    def _duplicates_must_be_removed(self, generation_number):
        if self.__badvalues_elim == "all":
            return True
        elif self.__badvalues_elim == "first":
            return (generation_number == 1)
        return False


    def show_best(self, population):
        # Get the best
        best_index = population.get_best_index()
        best_indiv = population.get_best_individual()
        lg.logger_.info("[APPLICATION] Proceed to show the best individual found.")
        lg.logger_.debug("[APPLICATION] Individual N#{0} - Cost: {1}".format(best_index, best_indiv.get_cost()))

        stop_no_graph = self._config.getboolean('BEHAVIOUR', 'stopongraph')
        EvaluatorFactory.get_callback().show_best(best_index, best_indiv, stop_no_graph)

    def _project_validations(self):
        # Check that the evaluation and preevaluation modules can be loaded
        EvaluatorFactory.get_callback()
        PreevaluationManager.get_callback()

    # TODO: Add another validations


class MLCCallbacksManager:
    def __init__(self):
        self.__callbacks = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.__callbacks:
            self.__callbacks[event_type] = []

        if not isinstance(callback, list):
            callback = [callback]

        self.__callbacks[event_type].extend(callback)

    def on_event(self, event_type, *args, **kwargs):
        if event_type not in self.__callbacks:
            return

        for callback in self.__callbacks[event_type]:
            callback(*args, **kwargs)