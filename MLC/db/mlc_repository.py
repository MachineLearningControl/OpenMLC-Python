from MLC.mlc_parameters.mlc_parameters import Config

class MLCRepository:
    _instance = None

    def get_individual(self, individual_id):
        raise NotImplementedError("MLCRepository::get_individual not implemented")

    def update_individual(self, individual_id, cost, ev_time=None):
        raise NotImplementedError("MLCRepository::update_individual not implemented")

    def add_individual(self, individual):
        raise NotImplementedError("MLCRepository::add_individual not implemented")

    @staticmethod
    def get_instance():
        # FIXME: use factories instead of this
        if MLCRepository._instance is None:
            if Config.get_instance().getboolean("BEHAVIOUR", "save"):
                raise Exception("SQLITE not implemented yet!!!")
            else:
                MLCRepository._instance = MemoryMLCRepository()

        return MLCRepository._instance


class MemoryMLCRepository(MLCRepository):
    def __init__(self):
        self._individuals = {}
        self._hashlist = {}
        self._costlist = {}
        self._last_indiv = 1

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