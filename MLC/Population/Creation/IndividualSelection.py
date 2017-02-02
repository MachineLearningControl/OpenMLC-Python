from BaseCreation import BaseCreation
from MLC.db.mlc_repository import MLCRepository


class IndividualSelection(BaseCreation):
    """
    Fill a Population with fixed Individuals.

    selected_individuals: dictionary containing {Individual: positions inside
    the first population}

    fill_creator: creator used to fill empty positions.

    Empty positions inside the Population will be completed using the neighbor individual,
    """

    def __init__(self, selected_individuals, fill_creator):
        BaseCreation.__init__(self)
        self.__fill_creator = fill_creator
        self.__selected_individuals = selected_individuals
        self.__individuals = []

    def create(self, gen_size):
        self.__fill_creator.create(gen_size)
        self.__individuals = self.__fill_creator.individuals()

        # Add Individuals
        for individual, positions in self.__selected_individuals.items():
            for position in positions:
                if position < gen_size:
                    individual_id, _ = MLCRepository.get_instance().add_individual(individual)
                    self.__individuals[position] = (position, individual_id)

    def individuals(self):
        return self.__individuals
