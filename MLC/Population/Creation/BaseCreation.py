import MLC.Log.log as lg
import numpy as np

from MLC.Common.PreevaluationManager import PreevaluationManager
from MLC.individual.Individual import Individual
from MLC.matlab_engine import MatlabEngine
from MLC.mlc_table.MLCTable import MLCTable
from MLC.mlc_parameters.mlc_parameters import Config


class BaseCreation(object):

    def __init__(self):
        self._eng = MatlabEngine.engine()
        self._config = Config.get_instance()

        # A list of tuples (index, number)
        self._individuals = []

    def create(self):
        raise NotImplementedError()

    def individuals(self):
        return self._individuals

    def _fill_creation(self, individuals, index, type):
        while index < len(individuals):
            indiv = Individual()
            indiv.generate(individual_type=type)
            response = MLCTable.get_instance().add_individual(indiv)

            if not response[1]:
                # The individual didn't exist
                indiv_number = individuals[index]

                lg.logger_.info('[FILL_CREATION] Generating individual N#' + str(indiv_number))
                lg.logger_.debug('[FILL_CREATION] Individual N#' + str(indiv_number) +
                                 ' - Value: ' + indiv.get_value())

                # Call the preevaluation function if it exists and if it is configured
                if self._config.getboolean('EVALUATOR', 'preevaluation'):
                    callback = PreevaluationManager.get_callback().preev
                    if callback is not None:
                        if not callback(indiv):
                            lg.logger_.info('[FILL_CREATION] Preevaluation failed'
                                            '. Individual value: ' + indiv.get_value())
                            continue

                self._individuals.append((index, response[0]))
                index += 1
            else:
                lg.logger_.debug('[FILL_CREATION] Replica created.')

        return index
