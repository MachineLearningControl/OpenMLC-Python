import MLC.Log.log as lg
import sys

from MLC.individual.Individual import Individual
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.db.mlc_repository import MLCRepository

class MLCTable:
    """
    Singleton that works as a wrapper for a MLCTable matlab class.
    """

    _instance = None

    def get_individual(self, individual_id):
        return MLCRepository.get_instance().get_individual(individual_id)

    def update_individual(self, individual_id, cost, ev_time=None):
        return MLCRepository.get_instance().update_individual(individual_id, cost, ev_time)

    def add_individual(self, individual):
        return MLCRepository.get_instance().add_individual(individual)

    def commit_changes(self):
        return MLCRepository.get_instance().commit_changes()

    @staticmethod
    def get_instance():
        if MLCTable._instance is None:
            # FIXME: Check later if this is right. We're not using the cascade
            # config parameter
            size = Config.get_instance().get_list('POPULATION', 'size')
            gen_size = size[0]

            MLCTable._instance = MLCTable()
        return MLCTable._instance
