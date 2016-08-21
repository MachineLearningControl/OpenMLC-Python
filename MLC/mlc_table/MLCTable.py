from MLC.matlab_engine import MatlabEngine
from MLC.individual.Individual import Individual

class MLCTable:
    """
    This works as a wrapper for a MLCTable matlab class.
    """
    def __init__(self, mlc_table):
        self._mlc_table = mlc_table

    def individuals(self, individual_id):
        individual = MatlabEngine.engine().get_individual(self._mlc_table,
                                                          individual_id)
        return Individual(mlc_ind=individual)

    def add_individual(self, individual):
        mlc_table, number = MatlabEngine.engine().add_individual(self._mlc_table,
                                                                 individual.get_matlab_object(),
                                                                 nargout=2)
        return MLCTable(mlc_table), number
