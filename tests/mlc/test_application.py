import unittest

from tests.test_helpers import TestHelper
from MLC.mlc_parameters.mlc_parameters import saved, Config

from MLC.Simulation import Simulation
from MLC.Application import Application, MLC_CALLBACKS


class ApplicationTest(unittest.TestCase):
    evaluations = 0

    @classmethod
    def setUpClass(cls):
        TestHelper.load_default_configuration()

    def test_callback_on_evaluate(self):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "10")
            Config.get_instance().set("BEHAVIOUR", "save", "false")


            def test_callback(individual_id, cost):
                ApplicationTest.evaluations += 1

            simulation = Simulation()
            app = Application(simulation, "testing", callbacks={MLC_CALLBACKS.ON_EVALUATE: test_callback})
            app.go(to_generation=2, fig=0, from_generation=0)
            self.assertEqual(ApplicationTest.evaluations, 2*10)