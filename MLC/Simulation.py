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

from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import Config


class Simulation:

    def __init__(self, experiment_name):
        MLCRepository.make(experiment_name)
        self._mlc_repository = MLCRepository.get_instance()

    def get_generation(self, generation):
        return self._mlc_repository.get_population(generation)

    def number_of_generations(self):
        return self._mlc_repository.count_population()

    def get_last_generation(self):
        if self.number_of_generations() == 0:
            raise IndexError("Empty simulation")
        return self._mlc_repository.get_population(self.number_of_generations())

    def add_generation(self, population):
        return self._mlc_repository.add_population(population)

    def erase_generations(self, from_generation):
        self._mlc_repository.remove_population_from(from_generation)

    @staticmethod
    def create_empty_population_for(generation):
        from MLC.Population.Population import Population

        cascade = Config.get_instance().get_list('OPTIMIZATION', 'cascade')
        size = Config.get_instance().get_list('POPULATION', 'size')

        population_size = cascade[1] if (generation > 1 and len(size) > 1) else size[0]
        population_subgenerations = 1 if cascade[1] == 0 else cascade[1]
        return Population(population_size, population_subgenerations, Config.get_instance(), MLCRepository.get_instance())