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
    def update_individual_cost(self, individual_id, cost):
        raise NotImplementedError("This method must be implemented")

    @staticmethod
    def get_instance():
        # FIXME: use factories instead of this
        if MLCRepository._instance is None:
            if Config.get_instance().getboolean("BEHAVIOUR", "save"):
                # lg.logger_.info("[MLC_REPOSITORY] Using DB as repository")
                from MLC.db.sqlite.sqlite_repository import SQLiteRepository
                db_name = Config.get_instance().get("BEHAVIOUR", "savedir")
                db_file = os.path.join(get_working_directory(), db_name)
                MLCRepository._instance = SQLiteRepository(db_file)
            else:
                # lg.logger_.info("[MLC_REPOSITORY] Using Memory as repository")
                MLCRepository._instance = MemoryMLCRepository()

        return MLCRepository._instance


class MemoryMLCRepository(MLCRepository):
    def __init__(self):
        self._individuals = {}
        self._individuals_data = {}
        self._hashlist = {}
        self._last_indiv = 1
        self._populations = []

    # operation over generations
    def add_population(self, population):
        self._populations.append(population)

        for index, indiv_id in enumerate(population._individuals):
            self._individuals_data[indiv_id]._add_data(len(self._populations),
                                                       population._costs[index],
                                                       population._ev_time[index])

        return len(self._populations)

    def remove_population(self, generation):
        del self._populations[generation-1]

    def get_population(self, generation):
        return self._populations[generation-1]

    def count_population(self):
        return len(self._populations)

    # special methods
    def remove_population_from(self, from_generation):
        del self._populations[from_generation-1:]

    # operations over individuals
    def add_individual(self, individual):
        hash = MLCRepositoryHelper.get_hash_for_individual(individual)

        # Check if the individual already exists comparing the hash value
        if hash in self._hashlist:
            return self._hashlist[hash], True

        self._individuals[self._last_indiv] = individual
        self._individuals_data[self._last_indiv] = IndividualData(individual.get_value())
        self._hashlist[hash] = self._last_indiv

        current_indiv = self._last_indiv
        self._last_indiv += 1

        return current_indiv, False

    def update_individual(self, individual_id, individual):
        try:
            self._individuals[individual_id] = individual
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def update_individual_cost(self, individual_id, cost):
        # TODO
        # ry:
        #    self._costlist[individual_id] = cost
        # except KeyError:
        #    raise KeyError("Individual N#%s does not exists" % individual_id)
        pass

    def remove_individual(self, individual_id):
        del self._individuals[individual_id]

    def get_individual(self, individual_id):
        try:
            return self._individuals[individual_id]
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def get_individual_data(self, individual_id):
        try:
            return self._individuals_data[individual_id]
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def count_individual(self):
        return len(self._individuals)