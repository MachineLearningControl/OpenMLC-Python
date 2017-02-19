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

import MLC.Log.log as lg
import numpy as np

from MLC.Common.PreevaluationManager import PreevaluationManager
from MLC.individual.Individual import Individual
from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import Config


class BaseCreation(object):

    def __init__(self):
        self._config = Config.get_instance()

        # A list of tuples (index, number)
        self._individuals = []

    def create(self, gen_size):
        raise NotImplementedError()

    def individuals(self):
        return self._individuals

    def _fill_creation(self, individuals, index, type):
        while index < len(individuals):
            indiv = Individual.generate(individual_type=type, config=Config.get_instance())
            response = MLCRepository.get_instance().add_individual(indiv)

            if not response[1]:
                # The individual didn't exist
                indiv_number = individuals[index]

                lg.logger_.info('[FILL_CREATION] Generating individual N#' + str(indiv_number))
                lg.logger_.debug('[FILL_CREATION] Individual N#' + str(indiv_number) +
                                 ' - Value: ' + indiv.get_value())

                # Call the preevaluation function if it exists and if it is configured
                if self._config.getboolean('EVALUATOR', 'preevaluation'):
                    callback = PreevaluationManager.get_callback().preev
                    if callback is not None:
                        if not callback(indiv):
                            lg.logger_.info('[FILL_CREATION] Preevaluation failed'
                                            '. Individual value: ' + indiv.get_value())
                            continue

                self._individuals.append((index, response[0]))
                index += 1
            else:
                lg.logger_.debug('[FILL_CREATION] Replica created.')

        return index
