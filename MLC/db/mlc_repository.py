import MLC.Log.log as lg

from MLC.mlc_parameters.mlc_parameters import Config
from MLC.config import get_working_directory
from collections import defaultdict
import hashlib
import os


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

    # operation over generations
    def add_population(self, population):
        raise NotImplementedError("This method must be implemented")

    def update_population(self, generation, population):
        raise NotImplementedError("This method must be implemented")

    def remove_population(self, generation):
        raise NotImplementedError("This method must be implemented")

    def get_population(self, generation):
        raise NotImplementedError("This method must be implemented")

    def count_population(self):
        raise NotImplementedError("This method must be implemented")

    # special methods
    def remove_population_from(self, from_generation):
        raise NotImplementedError("This method must be implemented")

    # operations over individuals
    def add_individual(self, individual):
        raise NotImplementedError("This method must be implemented")

    def update_individual(self, individual_id, individual):
        raise NotImplementedError("This method must be implemented")

    def remove_individual(self, individual_id):
        raise NotImplementedError("This method must be implemented")

    def get_individual(self, individual_id):
        raise NotImplementedError("This method must be implemented")

    def get_individual_data(self, individual_id):
        raise NotImplementedError("This method must be implemented")

    def count_individual(self):
        raise NotImplementedError("This method must be implemented")

    # special methods
    def update_individual_cost(self, individual_id, cost, evaluation_time, generation=-1):
        raise NotImplementedError("This method must be implemented")

    @staticmethod
    def get_instance():
        # FIXME: use factories instead of this
        if MLCRepository._instance is None:
            from MLC.db.sqlite.sqlite_repository import SQLiteRepository

            first_init = True

            if Config.get_instance().getboolean("BEHAVIOUR", "save"):
                db_name = Config.get_instance().get("BEHAVIOUR", "savedir")
                database = os.path.join(get_working_directory(), db_name)
                if os.path.exists(database):
                    first_init = False
            else:
                database = SQLiteRepository.IN_MEMORY_DB

            MLCRepository._instance = SQLiteRepository(database, init_db=first_init)

        return MLCRepository._instance