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

import hashlib
import MLC.Log.log as lg
import os

from MLC.config import get_working_directory
from MLC.mlc_parameters.mlc_parameters import Config
from collections import defaultdict


class MLCRepositoryHelper:

    @staticmethod
    def get_hash_for_individual(individual):
        m = hashlib.md5()
        m.update(individual.get_value())
        return m.hexdigest()


class IndividualData:
    """
        Global individual information:

        cost_history: map with the following structure {gen_number: [(cost, evaluation_time)]} where:

        gen_number:
            generation number
        cost:
            raw value returned by the evaluation function
        evaluation_time:
            date and time (on the computer clock) of sending of the indivs to the evaluation function
        appearances:
            number of time the individual appears
    """

    def __init__(self, value):
        self._value = value
        self._cost_history = defaultdict(list)
        self._appearances = 0

    def get_value(self):
        return self._value

    def get_appearances(self):
        return self._appearances

    def get_cost_history(self):
        return self._cost_history

    def _add_data(self, generation, cost, evaluation_time):
        self._cost_history[generation].append((cost, evaluation_time))
        self._appearances += 1


class MLCRepository:
    _instance = None

    # Close the Database opened
    def close():
        raise NotImplementedError("This method must be implemented")
    # operation over generations
    def add_population(self, population):
        raise NotImplementedError("This method must be implemented")

    def update_population(self, generation, population):
        raise NotImplementedError("This method must be implemented")

    def get_population(self, generation):
        raise NotImplementedError("This method must be implemented")

    def count_population(self):
        raise NotImplementedError("This method must be implemented")

    # special methods
    def remove_population_from(self, from_generation):
        raise NotImplementedError("This method must be implemented")

    def remove_population_to(self, to_generation):
        raise NotImplementedError("This method must be implemented")

    def remove_unused_individuals(self):
        raise NotImplementedError("This method must be implemented")

    # operations over individuals
    def add_individual(self, individual):
        raise NotImplementedError("This method must be implemented")

    def update_individual(self, individual_id, individual):
        raise NotImplementedError("This method must be implemented")

    def remove_individual(self, individual_id):
        raise NotImplementedError("This method must be implemented")

    def get_individual_with_min_cost_in_last_pop(self):
        raise NotImplementedError("This method must be implemented")

    def get_individual(self, individual_id):
        raise NotImplementedError("This method must be implemented")

    def get_individual_data(self, individual_id):
        raise NotImplementedError("This method must be implemented")

    def get_individuals_data(self):
        raise NotImplementedError("This method must be implemented")

    def count_individual(self):
        raise NotImplementedError("This method must be implemented")

    # special methods
    def update_individual_cost(self, individual_id, cost,
                               evaluation_time, generation=-1):
        raise NotImplementedError("This method must be implemented")

    # board configuration
    def save_board_configuration(self, board_config, board_id=None):
        raise NotImplementedError("This method must be implemented")

    def load_board_configuration(self, board_id):
        raise NotImplementedError("This method must be implemented")

    def save_connection(self, serial_connection, board_id, connection_id=None):
        raise NotImplementedError("This method must be implemented")

    def load_connection(self, connection_id):
        raise NotImplementedError("This method must be implemented")

    @staticmethod
    def get_instance():
        # FIXME: use factories instead of this
        if MLCRepository._instance is None:
            raise

        return MLCRepository._instance

    @staticmethod
    def make(experiment_name):
        """
        Create a new instance of the MLCRepository, no matter what it exists or not
        """
        from MLC.db.sqlite.sqlite_repository import SQLiteRepository
        first_init = True
        database = ""
        if Config.get_instance().getboolean("BEHAVIOUR", "save"):
            workspace_dir = get_working_directory()
            project_dir = os.path.join(workspace_dir, experiment_name)
            db_file_name = experiment_name + ".db"
            database = os.path.join(project_dir, db_file_name)
            first_init = not os.path.exists(database)
        else:
            database = SQLiteRepository.IN_MEMORY_DB

        MLCRepository._instance = SQLiteRepository(database, init_db=first_init)
