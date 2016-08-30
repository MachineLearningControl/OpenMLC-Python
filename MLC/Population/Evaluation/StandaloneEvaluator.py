import sys
import MLC.Log.log as lg


class StandaloneEvaluator(object):
    def __init__(self, eng, config, callback):
        self._eng = eng
        self._config = config
        self._callback = callback

    def evaluate(self, eval_idx, indivs, pop_number):
        jj = []

        for i in xrange(len(eval_idx)):
            index = eval_idx[i]
            lg.logger_.info('[POP][STAND_EVAL] Individual N#' + str(index) +
                            ' from generation ' + str(pop_number))

            indiv = self._eng.eval('wtable.individuals(' +
                                   str(indivs[index-1]) + ')')
            value = \
                self._eng.eval('wtable.individuals(' + str(indivs[index-1]) +
                               ').value')
            lg.logger_.debug('[POP][STAND_EVAL] Individual N#' + str(index) +
                             ' Value: ' + value)

            try:
                print indivs
                jj.append(self._callback(self._eng, self._config, indiv))
            except KeyError:
                lg.logger_.error("[POP][STAND_EVAL] Evaluation Function " +
                                 "doesn't exists. Aborting progam.")
                sys.exit(-1)

        return jj
