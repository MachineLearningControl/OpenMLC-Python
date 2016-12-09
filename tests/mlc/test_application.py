import unittest

from tests.test_helpers import TestHelper
from MLC.mlc_parameters.mlc_parameters import saved, Config

from MLC.Simulation import Simulation
from MLC.Application import Application, MLC_CALLBACKS

from MLC.db.mlc_repository import MLCRepository


class ApplicationTest(unittest.TestCase):
    on_start = 0
    on_start_counter_2 = 0
    on_evaluate = 0
    on_new_generation = []
    on_finish = 0

    @classmethod
    def setUpClass(cls):
        TestHelper.load_default_configuration()

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

            MLCRepository._instance = None
            simulation = Simulation()
            app = Application(simulation, "testing", callbacks={MLC_CALLBACKS.ON_START:          test_on_start_callback,
                                                                MLC_CALLBACKS.ON_EVALUATE:       test_on_evaluate_callback,
                                                                MLC_CALLBACKS.ON_NEW_GENERATION: test_on_new_generation_callback,
                                                                MLC_CALLBACKS.ON_FINISH:         test_on_finish_callback})
            app.go(to_generation=2, fig=0, from_generation=0)

            self.assertEqual(ApplicationTest.on_start,          1)
            self.assertEqual(ApplicationTest.on_evaluate,       2*10)
            self.assertEqual(ApplicationTest.on_new_generation, range(1, 2+1))
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

            MLCRepository._instance = None
            simulation = Simulation()
            start_callbacks = [test_on_start_callback, test_on_start_callback_increment_2]
            app = Application(simulation, "testing", callbacks={MLC_CALLBACKS.ON_START: start_callbacks})
            app.go(to_generation=2, fig=0, from_generation=0)

            self.assertEqual(ApplicationTest.on_start, 1)
            self.assertEqual(ApplicationTest.on_start_counter_2, 1)