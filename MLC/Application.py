import numpy as np
import MLC.Log.log as lg

from MLC.Common.PreevaluationManager import PreevaluationManager
from MLC.db.mlc_repository import MLCRepository
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Population.Creation.CreationFactory import CreationFactory
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.Simulation import Simulation


class MLC_CALLBACKS:
    ON_START = 0
    ON_EVALUATE = 1
    ON_NEW_GENERATION = 2
    ON_FINISH = 3


class Application(object):
    def __init__(self, simulation, callbacks={}):
        self._set_numpy_parameters()
        self._config = Config.get_instance()

        self._simulation = simulation
        self._mlc_repository = MLCRepository.get_instance()

        # Set logger mode of the App
        set_logger(self._config.get('LOGGING', 'logmode'))

        self._simulation = simulation
        self._project_validations()

        # callbacks configuration
        self.__callbacks_manager = MLCCallbacksManager()

        # bad values and duplicates
        self.__badvalues_elim = self._config.get('EVALUATOR', 'badvalues_elim')

        # Gen creator
        gen_method = self._config.get('GP', 'generation_method')
        self._gen_creator = CreationFactory.make(gen_method)

        # Gen evaluator
        ev_method = self._config.get('EVALUATOR', 'evaluation_method')

        self._evaluator = EvaluatorFactory.make(ev_method, self.__callbacks_manager)

        self._look_for_duplicates = self._config.getboolean('OPTIMIZATION', 'lookforduplicates')

        # callbacks for the MLC application
        if MLC_CALLBACKS.ON_START in callbacks:
            self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_START,
                                               callbacks[MLC_CALLBACKS.ON_START])

        if MLC_CALLBACKS.ON_EVALUATE in callbacks:
            self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_EVALUATE,
                                               callbacks[MLC_CALLBACKS.ON_EVALUATE])

        if MLC_CALLBACKS.ON_NEW_GENERATION in callbacks:
            self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_NEW_GENERATION,
                                               callbacks[MLC_CALLBACKS.ON_NEW_GENERATION])

        if MLC_CALLBACKS.ON_FINISH in callbacks:
            self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_FINISH,
                                               callbacks[MLC_CALLBACKS.ON_FINISH])

        # add callback to show best individual
        self.__callbacks_manager.subscribe(MLC_CALLBACKS.ON_NEW_GENERATION, self.show_best)
        self.__display_best = False

    def _set_numpy_parameters(self):
        # Set printable resolution (don't alter numpy interval resolution)
        np.set_printoptions(precision=3)
        # Show full arrays, no matter what size do they have
        np.set_printoptions(threshold=np.inf)
        # Don't show scientific notation
        np.set_printoptions(suppress=True)
        # Transform printed warnings to real warnings
        np.seterr(all='raise')

    def go(self, to_generation, from_generation=None, display_best=False):
        """
        Start MLC2 problem solving (MLC2 Toolbox)

        :param to_generation: creates (if necessary) the population, evaluate
            and  evolve it until to_generation evaluated generations are
            obtained.

        :param from_generation: first generation must be evolved from
        from_generation, takes last generation as default value.

        :param display_best: displays the best individual if implemented
        in the evaluation function at the end of each generation evaluation.

        :return:
        """
        self.__display_best = display_best

        if from_generation is None:
            from_generation = self._mlc_repository.count_population()

        lg.logger_.info("Running MLC from generation %s to %s" % (from_generation, to_generation))

        if from_generation < self._mlc_repository.count_population():
            lg.logger_.info("Generations %s to %s discarded" % (from_generation+1, self._mlc_repository.count_population()))
            self._mlc_repository.remove_population_from(from_generation+1)

        # emit app start event
        self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_START)

        # First generation must be generated from scratch
        if self._mlc_repository.count_population() == 0:
            lg.logger_.info("Creating and filling first generation")

            last_population = Simulation.create_empty_population_for(1)
            last_population.fill(self._gen_creator)
            self.evaluate_population(last_population, 1)
            self._mlc_repository.add_population(last_population)

            # emit new generation event
            self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_NEW_GENERATION, 1)
            lg.logger_.info("Population created. Number: %s - Size: %s" % (1, last_population.get_size()))

        while self._mlc_repository.count_population() < to_generation:
            last_generation = self._mlc_repository.count_population()
            last_population = self._mlc_repository.get_population(last_generation)

            # obtain the next generation by evolving the lastone
            lg.logger_.info("Evolving to Population %s using population %s" % (last_generation+1, last_generation))

            next_population = Simulation.create_empty_population_for(last_generation+1)
            next_population = last_population.evolve(next_population)

            # continue with evolve if there are duplicated individuals
            if self._look_for_duplicates:
                while next_population.remove_duplicates() > 0:
                    next_population = last_population.evolve(next_population)

            # evaluate population
            self.evaluate_population(next_population, last_generation)

            lg.logger_.info("Population created. Number: %s - Size: %s" % (last_generation + 1, next_population.get_size()))
            self._mlc_repository.add_population(next_population)

            # emit new generation event
            self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_NEW_GENERATION, last_generation+1)

        lg.logger_.info("MLC Simulation Finished")

        # emit app finish event
        self.__callbacks_manager.on_event(MLC_CALLBACKS.ON_FINISH)

    def get_simulation(self):
        return self._simulation

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

    def show_best(self, generation_number):
        if self.__display_best:
            show_all = self._config.getboolean('BEHAVIOUR', 'showeveryitbest')
            stop_on_graph = self._config.getboolean('BEHAVIOUR', 'stopongraph')

            population = self._mlc_repository.get_population(generation_number)
            best_index, best_indiv, cost = population.get_best_individual()

            EvaluatorFactory.get_callback().show_best(best_index, best_indiv, cost, stop_on_graph)

    def _project_validations(self):
        # Check that the evaluation and preevaluation modules can be loaded
        EvaluatorFactory.get_callback()
        PreevaluationManager.get_callback()


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