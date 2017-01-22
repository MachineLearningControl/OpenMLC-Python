import unittest
from tests.test_helpers import TestHelper

from MLC.mlc_parameters.mlc_parameters import saved, Config
from MLC.Population.Population import Population
from MLC.db.mlc_repository import MLCRepository
from MLC.Population.Creation.IndividualSelection import IndividualSelection
from MLC.individual.Individual import Individual


class PopulationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestHelper.load_default_configuration()

    def test_add_one_individual(self):
        creator = IndividualSelection({Individual("1+1"): [0, 1, 2, 3, 4]})

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1, 1, 1, 1, 1],
                               expected_individuals={1: Individual("1+1")})

    def test_add_one_individual_incomplete_population(self):
        creator = IndividualSelection({Individual("1+1"): [0]})

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1, 1, 1, 1, 1],
                               expected_individuals={1: Individual("1+1")})

    def test_add_multiple_individuals(self):
        creator = IndividualSelection({Individual("1+1"): [0, 1, 2],
                                       Individual("2+2"): [3, 4]})

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1, 1, 1, 2, 2],
                               expected_individuals={1: Individual("1+1"),
                                                     2: Individual("2+2")})

    def test_add_more_individuals_than_the_gensize(self):
        creator = IndividualSelection({Individual("1+1"): [0, 1, 2, 3, 4, 5, 6, 7]})

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1, 1, 1, 1, 1],
                               expected_individuals={1: Individual("1+1")})

    def test_add_individuals_fill_empty_spaces(self):
        creator = IndividualSelection({Individual("1+1"): [0, 4],
                                       Individual("2+2"): [2]})

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1, 1, 2, 2, 1],
                               expected_individuals={1: Individual("1+1"),
                                                     2: Individual("2+2")})

    def test_add_individuals_out_of_gen_not_inserted(self):
        creator = IndividualSelection({Individual("1+1"): [0, 1, 2, 3, 4],
                                       Individual("2+2"): [5, 6, 7]})

        self.__fill_and_assert(fill_creator=creator,
                               expected_pop_indexes=[1, 1, 1, 1, 1],
                               expected_individuals={1: Individual("1+1")})

    def __fill_and_assert(self, fill_creator, expected_pop_indexes, expected_individuals):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "5")
            Config.get_instance().set("BEHAVIOUR", "save", "false")

            population = Population(5, 0, Config.get_instance(), MLCRepository.make(""))
            population.fill(fill_creator)
            MLCRepository.get_instance().add_population(population)

            # Assert that one Population was added
            self.assertEqual(MLCRepository.get_instance().count_population(), 1)

            # Assert that all expected individuals were created
            self.assertEqual(MLCRepository.get_instance().count_individual(), len(expected_individuals))

            # Assert that the individuals are in the expected position inside the Population
            for position, i in enumerate(expected_pop_indexes):
                expected_individual = expected_individuals[i]
                inserted_individual_id = population.get_individuals()[position]
                inserted_individual = MLCRepository.get_instance().get_individual(inserted_individual_id)

                self.assertEqual(expected_individual.get_value(), inserted_individual.get_value())

            # Assert all individuals are created
            created_individuals = [MLCRepository.get_instance().get_individual(i).get_value() for i in range(1, len(expected_individuals)+1)]
            for _, individual in expected_individuals.items():
                self.assertIn(individual.get_value(), created_individuals)
