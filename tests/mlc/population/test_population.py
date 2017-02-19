# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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

