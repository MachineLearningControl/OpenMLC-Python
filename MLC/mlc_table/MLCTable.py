from MLC.matlab_engine import MatlabEngine
from MLC.individual.Individual import Individual

class MLCTable:
    @staticmethod
    def get_individual(mlctable, individual_id):
        individual = MatlabEngine.engine().get_individual(mlctable, individual_id)
        return Individual(mlc_ind=individual)

    @staticmethod
    def add_individual(mlctable, new_ind):
        return MatlabEngine.engine().add_individual(mlctable,
                                                    new_ind.get_matlab_object(),
                                                    nargout=2)