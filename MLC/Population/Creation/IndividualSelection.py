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

from MLC.Population.Creation.BaseCreation import BaseCreation
from MLC.db.mlc_repository import MLCRepository


class IndividualSelection(BaseCreation):
    """
    Fill a Population with fixed Individuals.

    selected_individuals: dictionary containing {Individual: positions inside
    the first population}

    fill_creator: creator used to fill empty positions.

    Empty positions inside the Population will be completed using the neighbor individual,
    """

    def __init__(self, selected_individuals, fill_creator):
        BaseCreation.__init__(self)
        self.__fill_creator = fill_creator
        self.__selected_individuals = selected_individuals
        self.__individuals = []

    def create(self, gen_size):
        self.__fill_creator.create(gen_size)
        self.__individuals = self.__fill_creator.individuals()

        # Add Individuals
        for individual, positions in self.__selected_individuals.items():
            for position in positions:
                if position < gen_size:
                    individual_id, _ = MLCRepository.get_instance().add_individual(individual)
                    self.__individuals[position] = (position, individual_id)

    def individuals(self):
        return self.__individuals
