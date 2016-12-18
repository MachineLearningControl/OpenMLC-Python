from MLC.mlc_parameters.mlc_parameters import Config


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
    def remove_population(self, from_generation):
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
        self._populations = []

    # operation over generations
    def add_population(self, population):
        self._populations.append(population)
        return len(self._populations)

    def update_population(self, generation, population):
        self._populations[generation-1] = population

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
        # Check if the individual already exists comparing the hash value
        if individual.get_hash() in self._hashlist:
            return self._hashlist[individual.get_hash()], True

        self._individuals[self._last_indiv] = individual
        self._hashlist[individual.get_hash()] = self._last_indiv
        self._costlist[self._last_indiv] = individual.get_cost()

        current_indiv = self._last_indiv
        self._last_indiv += 1

        return current_indiv, False

    def update_individual(self, individual_id, individual):
        try:
            self._individuals[individual_id] = individual
            self._costlist[individual_id] = individual.get_cost()
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def update_individual_cost(self, individual_id, cost):
        try:
            self._costlist[individual_id] = cost
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def remove_individual(self, individual_id):
        del self._individuals[individual_id]

    def get_individual(self, individual_id):
        try:
            return self._individuals[individual_id]
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def count_individual(self):
        return len(self._individuals)