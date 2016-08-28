import MLC.Log.log as lg
import sys

from MLC.matlab_engine import MatlabEngine
from MLC.individual.Individual import Individual
from MLC.mlc_parameters.mlc_parameters import Config


class MLCTable:
    """
    Singleton that works as a wrapper for a MLCTable matlab class.
    """

    _instance = None

    def __init__(self, mlc_table):
        self._mlc_table = mlc_table
        self._individuals = {}
        # Key: Hash - Value: Individual index
        self._hashlist = {}
        self._costlist = {}
        self._last_indiv = 1

    def get_individual(self, individual_id):
        """
        individual = MatlabEngine.engine().get_individual(self._mlc_table,
                                                          individual_id)
        """
        try:
            return self._individuals[individual_id]
        except KeyError:
            lg.logger_.error("[MLC_TABLE] get_individual - Individual does not exists. Indiv N#:" + str(individual_id))
            raise

    def update_individual(self, individual_id, cost, ev_time=None):
        try:
            indiv = self._individuals[individual_id]
            indiv.set_cost(cost)
            self._costlist[individual_id] = cost
        except KeyError:
            lg.logger_.error("[MLC_TABLE] update_individual - Individual does not exists. Indiv N#:" + str(individual_id))
            raise
            # sys.exit(-1)

    def add_individual(self, individual):
        """
        mlc_table, number, already_exists = MatlabEngine.engine().add_individual(self._mlc_table,
                                                                                 individual.get_matlab_object(),
                                                                                 nargout=3)
        """

        # Check if the individual already exists comparing the hash value
        if individual.get_hash() in self._hashlist:
            indiv_index = self._hashlist[individual.get_hash()]
            return indiv_index, True

        self._individuals[self._last_indiv] = individual
        self._hashlist[individual.get_hash()] = self._last_indiv
        self._costlist[self._last_indiv] = individual.get_cost()

        current_indiv = self._last_indiv
        self._last_indiv += 1

        return current_indiv, False

    def get_matlab_object(self):
        return self._mlc_table

    @staticmethod
    def get_instance():
        if MLCTable._instance is None:
            # FIXME: Check later if this is right. We're not using the cascade
            # config parameter
            size = Config.get_instance().get_list('POPULATION', 'size')
            gen_size = size[0]

            table = MatlabEngine.engine().MLCtable(int(gen_size) * 50)
            MLCTable._instance = MLCTable(table)
        return MLCTable._instance
