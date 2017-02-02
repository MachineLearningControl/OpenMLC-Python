import unittest
from tests.test_helpers import TestHelper

from MLC.mlc_parameters.mlc_parameters import saved, Config
from MLC.Population.Population import Population
from MLC.db.mlc_repository import MLCRepository
from MLC.Population.Creation.IndividualSelection import IndividualSelection
from MLC.Population.Creation.MixedRampedGauss import MixedRampedGauss
from MLC.individual.Individual import Individual


class PopulationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestHelper.load_default_configuration()

    def test_add_one_individual(self):

        base_creator = MixedRampedGauss()
        creator = IndividualSelection({Individual("1+1"): [0, 1, 2, 3, 4]}, base_creator)

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1, 1, 1, 1, 1],
                               expected_individuals={1: Individual("1+1")})

    def test_add_one_individual_incomplete_population(self):
        base_creator = MixedRampedGauss()
        creator = IndividualSelection({Individual("1+1"): [0]}, base_creator)

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1],
                               expected_individuals={1: Individual("1+1")})

    def __fill_and_assert(self, fill_creator, expected_pop_indexes, expected_individuals):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "5")
            Config.get_instance().set("BEHAVIOUR", "save", "false")
            from MLC.Log.log import set_logger
            set_logger('testing')

            population = Population(5, 0, Config.get_instance(), MLCRepository.make(""))
            population.fill(fill_creator)
            MLCRepository.get_instance().add_population(population)

            # Assert that one Population was added
            self.assertEqual(MLCRepository.get_instance().count_population(), 1)

            # Assert that the individuals are in the expected position inside the Population
            for position, i in enumerate(expected_pop_indexes):
                expected_individual = expected_individuals[i]
                inserted_individual_id = population.get_individuals()[position]
                inserted_individual = MLCRepository.get_instance().get_individual(inserted_individual_id)

                self.assertEqual(expected_individual.get_value(), inserted_individual.get_value())

