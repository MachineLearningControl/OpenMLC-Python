import sys
import MLC.Log.log as lg

from MLC.matlab_engine import MatlabEngine
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.mlc_table.MLCTable import MLCTable


class StandaloneEvaluator(object):

    def __init__(self, callback):
        self._eng = MatlabEngine.engine()
        self._config = Config.get_instance()
        self._callback = callback

    def evaluate(self, indivs, pop_number):
        jj = []

        for index in indivs:
            lg.logger_.info('[POP][STAND_EVAL] Individual N#' + str(index) +
                            ' from generation ' + str(pop_number))

            # Retrieve the individual to be evaluated
            py_indiv = MLCTable.get_individual(index)
            lg.logger_.debug('[POP][STAND_EVAL] Individual N#' + str(index) +
                             ' Value: ' + py_indiv.get_value())

            try:
                jj.append(self._callback(self._eng, self._config, py_indiv))
            except KeyError:
                lg.logger_.error("[POP][STAND_EVAL] Evaluation Function " +
                                 "doesn't exists. Aborting progam.")
                sys.exit(-1)

        return jj
