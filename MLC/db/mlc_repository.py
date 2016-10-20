from MLC.mlc_parameters.mlc_parameters import Config

class MLCRepository:
    _instance = None

    def add_population(self, population):
        raise NotImplementedError("MLCRepository::add_population not implemented")

    def get_populations(self):
        raise NotImplementedError("MLCRepository::get_populations not implemented")

    def get_individual(self, individual_id):
        raise NotImplementedError("MLCRepository::get_individual not implemented")

    def update_individual(self, individual_id, cost, ev_time=None):
        raise NotImplementedError("MLCRepository::update_individual not implemented")

    def add_individual(self, individual):
        raise NotImplementedError("MLCRepository::add_individual not implemented")

    def number_of_individuals(self):
        raise NotImplementedError("MLCRepository::number_of_individuals not implemented")

    def erase_generations(self, from_generation):
        raise NotImplementedError("MLCRepository::erase_generations not implemented")

    def remove_individuals(self, individuals):
        raise NotImplementedError("MLCRepository::remove_individuals not implemented")

    def commit_changes(self):
        pass

    @staticmethod
    def get_instance():
        # FIXME: use factories instead of this
        if MLCRepository._instance is None:
            if Config.get_instance().getboolean("BEHAVIOUR", "save"):
                from MLC.db.sqlite.sqlite_repository import SQLiteRepository
                MLCRepository._instance = SQLiteRepository()
            else:
                MLCRepository._instance = MemoryMLCRepository()

        return MLCRepository._instance


class MemoryMLCRepository(MLCRepository):
    def __init__(self):
        self._individuals = {}
        self._hashlist = {}
        self._costlist = {}
        self._last_indiv = 1
        self._populations = {}

    def add_population(self, population):
        pass

    def erase_generations(self, from_generation):
        pass

    def get_populations(self):
        return []

    def remove_individuals(self, individuals):
        for individual in individuals:
            del self._individuals[individual]

    def get_individual(self, individual_id):
        try:
            return self._individuals[individual_id]
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def update_individual(self, individual_id, cost, ev_time=None):
        try:
            self._individuals[individual_id].set_cost(cost)
            self._costlist[individual_id] = cost
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def add_individual(self, individual):
        # Check if the individual already exists comparing the hash value
        if individual.get_hash() in self._hashlist:
            return self._hashlist[individual.get_hash()], True

        self._individuals[self._last_indiv] = individual
        self._hashlist[individual.get_hash()] = self._last_indiv
        self._costlist[self._last_indiv] = individual.get_cost()

        current_indiv = self._last_indiv
        self._last_indiv += 1

        return current_indiv, False

    def number_of_individuals(self):
        return len(self._individuals)