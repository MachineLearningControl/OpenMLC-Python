from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import Config


class Simulation:

    def __init__(self):
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