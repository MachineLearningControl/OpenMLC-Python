import shutil
import os
import unittest

from MLC.Population.Creation import BaseCreation
from tests.test_helpers import TestHelper
from MLC.config import get_working_directory
from MLC.config import get_test_path
from MLC.mlc_parameters.mlc_parameters import saved, Config
from MLC.api.MLCLocal import MLCLocal

from MLC.Simulation import Simulation
from MLC.Application import Application, MLC_CALLBACKS

from MLC.db.mlc_repository import MLCRepository


class ApplicationTest(unittest.TestCase):
    on_start = 0
    on_start_counter_2 = 0
    on_evaluate = 0
    on_new_generation = []
    on_finish = 0
    experiment_name = "test_application"
    workspace_dir = os.path.join(get_working_directory(), "workspace")
    test_conf_path = os.path.join(get_test_path(), TestHelper.DEFAULT_CONF_FILENAME)
    experiment_dir = os.path.join(workspace_dir, experiment_name)
    mlc_local = None

    @classmethod
    def setUpClass(cls):
        TestHelper.load_default_configuration()
        # Create the MLC workspace dir of this tests
        os.makedirs(ApplicationTest.workspace_dir)

        # Create the MLCLocal and the workspace of MLC, and create
        # a new experiment to be used to test the callbacks
        ApplicationTest.mlc_local = MLCLocal(ApplicationTest.workspace_dir)

    @classmethod
    def tearDownClass(cls):
        # Erase the MLC workspace dir of this tests
        shutil.rmtree(ApplicationTest.workspace_dir)

    def test_callback_on_evaluate(self):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "10")
            Config.get_instance().set("BEHAVIOUR", "save", "false")

            def test_on_start_callback():
                ApplicationTest.on_start += 1

            def test_on_evaluate_callback(individual_id, cost):
                ApplicationTest.on_evaluate += 1

            def test_on_new_generation_callback(generation_number):
                ApplicationTest.on_new_generation.append(generation_number)

            def test_on_finish_callback():
                ApplicationTest.on_finish += 1

            callbacks_dict = {MLC_CALLBACKS.ON_START:          test_on_start_callback,
                              MLC_CALLBACKS.ON_EVALUATE:       test_on_evaluate_callback,
                              MLC_CALLBACKS.ON_NEW_GENERATION: test_on_new_generation_callback,
                              MLC_CALLBACKS.ON_FINISH:         test_on_finish_callback}

            ApplicationTest.mlc_local.new_experiment(ApplicationTest.experiment_name,
                                                     ApplicationTest.test_conf_path)
            ApplicationTest.mlc_local.open_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.go(experiment_name=ApplicationTest.experiment_name,
                                         to_generation=2,
                                         from_generation=0,
                                         callbacks=callbacks_dict)
            ApplicationTest.mlc_local.close_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.delete_experiment(ApplicationTest.experiment_name)

            self.assertEqual(ApplicationTest.on_start,          1)
            self.assertEqual(ApplicationTest.on_evaluate,       2 * 10)
            self.assertEqual(ApplicationTest.on_new_generation, range(1, 2 + 1))
            self.assertEqual(ApplicationTest.on_finish,         1)

    def test_list_of_callbacks(self):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "10")
            Config.get_instance().set("BEHAVIOUR", "save", "false")

            ApplicationTest.on_start = 0
            ApplicationTest.on_start_counter_2 = 0

            def test_on_start_callback():
                ApplicationTest.on_start += 1

            def test_on_start_callback_increment_2():
                ApplicationTest.on_start_counter_2 += 1

            start_callbacks = [test_on_start_callback, test_on_start_callback_increment_2]

            ApplicationTest.mlc_local.new_experiment(ApplicationTest.experiment_name,
                                                     ApplicationTest.test_conf_path)
            ApplicationTest.mlc_local.open_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.go(experiment_name=ApplicationTest.experiment_name,
                                         to_generation=2,
                                         from_generation=0,
                                         callbacks={MLC_CALLBACKS.ON_START: start_callbacks})
            ApplicationTest.mlc_local.close_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.delete_experiment(ApplicationTest.experiment_name)

            self.assertEqual(ApplicationTest.on_start, 1)
            self.assertEqual(ApplicationTest.on_start_counter_2, 1)

    def test_set_custom_gen_creator(self):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "5")
            Config.get_instance().set("BEHAVIOUR", "save", "false")

            from MLC.Population.Creation.BaseCreation import BaseCreation
            from MLC.individual.Individual import Individual

            class TestCreator(BaseCreation):
                def __init__(self):
                    BaseCreation.__init__(self)

                def create(self, gen_size):
                    MLCRepository.get_instance().add_individual(Individual("(root 1)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 2)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 3)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 4)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 5)"))

                def individuals(self):
                    return [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]

            simulation = Simulation("")
            mlc = Application(simulation, gen_creator=TestCreator())
            mlc.go(to_generation=1)

            # Assert first Population was filled using the TestCreator
            population = MLCRepository.get_instance().get_population(1)
            self.assertEqual(population.get_individuals(), [1, 2, 3, 4, 5])

