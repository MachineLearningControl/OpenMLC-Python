import sys
import MLC.Log.log as lg

from MLC.mlc_parameters.mlc_parameters import Config
from MLC.mlc_table.MLCTable import MLCTable


class StandaloneEvaluator(object):

    def __init__(self, callback, callback_manager):
        self._config = Config.get_instance()
        self._callback = callback
        self._callback_manager = callback_manager

    def evaluate(self, indivs):
        jj = []

        lg.logger_.info("Evaluating %s individuals" % len(indivs))

        for index in indivs:
            lg.logger_.debug('[POP][STAND_EVAL] Individual N#' + str(index))

            # Retrieve the individual to be evaluated
            py_indiv = MLCTable.get_instance().get_individual(index)
            lg.logger_.debug('[POP][STAND_EVAL] Individual N#' + str(index) +
                             ' Value: ' + py_indiv.get_value())

            try:
                cost = self._callback.cost(py_indiv)
                jj.append(cost)

                from MLC.Application import MLC_CALLBACKS
                self._callback_manager.on_event(MLC_CALLBACKS.ON_EVALUATE, index, cost)

            except KeyError:
                lg.logger_.error("[POP][STAND_EVAL] Evaluation Function " +
                                 "doesn't exists. Aborting progam.")
                sys.exit(-1)

        return jj
