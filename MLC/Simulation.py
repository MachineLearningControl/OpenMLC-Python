from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import Config


class Simulation:
    def __init__(self):
        self._generations = MLCRepository.get_instance().get_populations()

    def get_generation(self, gen):
        if gen > len(self._generations):
            raise IndexError("Generation %s do not exist" % gen)
        return self._generations[gen-1]

    def generations(self):
        return len(self._generations)

    def get_last_generation(self):
        if len(self._generations) == 0:
            raise IndexError("Empty simulation")
        return self._generations[self.generations()-1]

    def add_next_generation(self, population):
        self._generations.append(population)
        return len(self._generations)

    @staticmethod
    def get_population_size(generation):
        cascade = Config.get_instance().get_list('OPTIMIZATION', 'cascade')
        size = Config.get_instance().get_list('POPULATION', 'size')
        return cascade[1] if (generation > 1 and len(size) > 1) else size[0]

    @staticmethod
    def get_subgenerations(generation):
        cascade = Config.get_instance().get_list('OPTIMIZATION', 'cascade')
        return 1 if cascade[1] == 0 else cascade[1]