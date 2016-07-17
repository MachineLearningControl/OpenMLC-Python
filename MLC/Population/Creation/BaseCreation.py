import MLC.Log.log as lg
import numpy as np

from MLC.individual.Individual import Individual


class BaseCreation(object):
    def __init__(self, eng, config):
        self._eng = eng
        self._config = config

        # A list of tuples (index, number)
        self._individuals = []

    def create(self):
        raise NotImplementedError()

    def individuals(self):
        return self._individuals

    def _fill_creation(self, individuals, index, type):
        while index < len(individuals):

            indiv = Individual()
            param = self._eng.eval('wmlc.parameters')
            indiv.generate(param, type)

            table = self._eng.eval('wtable')
            # Returns (individual, number, repeated)
            response = self._eng.add_individual(table, indiv.get_matlab_object(), nargout=3)

            if not response[2]:
                # The individual didn't exist
                indiv_number = individuals[response[1] - 1]

                lg.logger_.info('[FILL_CREATION] Generating individual N#' +
                                str(indiv_number))

                self._eng.workspace['windiv'] = indiv.get_matlab_object()
                lg.logger_.debug('[FILL_CREATION] Individual N#' +
                                 str(indiv_number) +
                                 ' - Value: ' + self._eng.eval('windiv.value'))

                if self._eng.preev(indiv.get_matlab_object(), param, nargout=1):
                    self._individuals.append((index, response[1]))
                    index += 1
                else:
                    lg.logger_.info('[FILL_CREATION] Preevaluation failed'
                                    '. Individual value: ' +
                                    self._eng.eval('windiv.value'))
            else:
                lg.logger_.debug('[FILL_CREATION] Replica created.')

        return index
