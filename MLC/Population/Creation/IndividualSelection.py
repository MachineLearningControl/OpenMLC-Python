from BaseCreation import BaseCreation
from MLC.db.mlc_repository import MLCRepository


class IndividualSelection(BaseCreation):
    """
    Fill a Population with fixed Individuals.

    selected_individuals: dictionary containing {Individual: positions inside
    the first population}

    Empty positions inside the Population will be completed using the neighbor individual,
    """

    def __init__(self, selected_individuals):
        BaseCreation.__init__(self)
        self.__selected_individuals = selected_individuals
        self.__individuals = []

    def create(self, gen_size):
        self.__individuals = [-1] * gen_size

        # Add Individuals
        for individual, positions in self.__selected_individuals.items():
            for position in positions:
                if position < gen_size:
                    individual_id, _ = MLCRepository.get_instance().add_individual(individual)
                    self.__individuals[position] = individual_id

        # Fill empty spaces
        for index, indiv_id in enumerate(self.__individuals):
            if indiv_id == -1:
                if index > 0:
                    self.__individuals[index] = self.__individuals[index - 1]
                else:
                    self.__individuals[index] = self.__individuals[index + 1]

    def individuals(self):
        return enumerate(self.__individuals)
