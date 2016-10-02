from __builtin__ import staticmethod

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
from MLC.db.mlc_repository import MLCRepository
from MLC.Simulation import Simulation
from MLC.Population.Creation.CreationFactory import CreationFactory


class Application(object):

    def __init__(self, simulation, log_mode='console'):
        self._eng = MatlabEngine.engine()
        self._config = Config.get_instance()
        self._set_ev_callbacks()
        self._set_preev_callbacks()

        # Set logger mode of the App
        set_logger(log_mode)
        self._simulation = simulation

        # gen creator
        gen_method = self._config.get('GP', 'generation_method')
        self._gen_creator = CreationFactory.make(gen_method)

        self._show_all_bests = self._config.getboolean('BEHAVIOUR', 'showeveryitbest')
        self._look_for_duplicates = self._config.getboolean('OPTIMIZATION', 'lookforduplicates')

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
            raise Exception("Amounts of generations must be a positive number, provided: %s" % ngen)

        # First generation must be generated from scratch
        if self._simulation.number_of_generations() == 0:
            first_population = Population(Simulation.get_population_size(1), Simulation.get_subgenerations(1), 1)
            self._simulation.add_generation(first_population)

        while self._simulation.number_of_generations() < ngen:
            current_population = self._simulation.get_last_generation()
            generation_number = self._simulation.number_of_generations()+1

            # create
            if not current_population.is_complete():
                current_population.fill(self._gen_creator)

            # evaluate
            self.evaluate_population(current_population, generation_number)

            # show best if necessary
            if (self._simulation.number_of_generations() >= ngen or self._show_all_bests) and fig > 0:
                self.show_best()

            # evolve
            next_population = current_population.evolve()
            while self._look_for_duplicates and next_population.remove_duplicates() > 0:
                next_population = current_population.evolve(next_population)

            # save new generation
            self._simulation.add_generation(next_population)
            MLCTable.get_instance().commit_changes()

        # Evaluate last population
        self.evaluate_population(self._simulation.get_last_generation(),
                                 self._simulation.number_of_generations())
        self.show_best(self._simulation.get_last_generation())
        MLCTable.get_instance().commit_changes()

        for i in range(self._simulation.number_of_generations()):
            p = self._simulation.get_generation(i)
            MLCRepository.get_instance().add_population(p)

    def get_simulation(self):
        return self._simulation

    def get_population(self, number):
        return self._pop_container[number]

    def evaluate_population(self, population, generation_number):
        # First evaluation
        population.evaluate()

        # Remove bad individuals
        if self._duplicates_must_be_removed(generation_number):
            while population.remove_bad_individuals():
                # There are bad individuals, recreate the population
                population.fill(self._gen_creator)
                population.evaluate()

        population.sort()

        # Enforce reevaluation
        if self._config.getboolean('EVALUATOR', 'ev_again_best'):
            ev_again_times = self._config.getint('EVALUATOR', 'ev_again_times')
            for i in range(1, ev_again_times):
                ev_again_nb = self._config.getint('EVALUATOR', 'ev_again_nb')
                population.evaluate()
                population.sort()

    def evolve_population(self, population, look_for_duplicates):
        next_pop = population.evolve()

        if look_for_duplicates:
            while next_pop.remove_duplicates() > 0:
                next_pop = population.evolve(next_pop)

        return next_pop

    def _duplicates_must_be_removed(self, generation_number):
        bad_values = self._config.get('EVALUATOR', 'badvalues_elim')
        must_be_removed = False

        if bad_values == "all":
            must_be_removed = True

        elif bad_values == "first":
            must_be_removed = (generation_number == 1)

        return must_be_removed

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
