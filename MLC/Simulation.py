from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import Config


class Simulation:

    def __init__(self):
        self._generations = MLCRepository.get_instance().get_populations()

    def get_generation(self, generation):
        if generation <= 0:
            raise IndexError("Generation must start from 1, obtain %s" % generation)

        if generation > len(self._generations):
            raise IndexError("Generation %s does not exist" % generation)

        return self._generations[generation - 1]

    def number_of_generations(self):
        return len(self._generations)

    def get_last_generation(self):
        if len(self._generations) == 0:
            raise IndexError("Empty simulation")
        return self._generations[self.number_of_generations() - 1]

    def add_generation(self, population):
        self._generations.append(population)
        return len(self._generations)

    def erase_generations(self, from_generation):
        if from_generation > 0:
            self._generations = self._generations[:from_generation - 1]
            MLCRepository.get_instance().erase_generations(from_generation)

    @staticmethod
    def create_empty_population_for(generation):
        from MLC.Population.Population import Population

        cascade = Config.get_instance().get_list('OPTIMIZATION', 'cascade')
        size = Config.get_instance().get_list('POPULATION', 'size')

        population_size = cascade[1] if (generation > 1 and len(size) > 1) else size[0]
        population_subgenerations = 1 if cascade[1] == 0 else cascade[1]
        return Population(population_size, population_subgenerations, generation, Config.get_instance(), MLCRepository.get_instance())
