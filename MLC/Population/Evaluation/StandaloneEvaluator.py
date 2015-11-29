import MLC.Log.log as lg
import numpy as np


class StandaloneEvaluator(object):
    def __init__(self, eng, config):
        self._eng = eng
        self._config = config

    def evaluate(self, eval_index, pop_number):
        # TODO: Don't use this value as a callback for the moment. Hardcode
        # the call to the evaluation function
        eval_function = self._config.get('EVALUATOR', 'evaluation_function')
        JJ = []

        for i in xrange(1,len(eval_index)+1):
            lg.logger_.debug('Individual N#' + str(i) +
                             ' from generation ' + str(pop_number))

            indiv = self._eng.eval('wtable.individuals(' + str(i) + ')')
            value = \
                self._eng.eval('wtable.individuals(' + str(i) + ').value')
            lg.logger_.debug(value)
            JJ.append(self._toy_problem(indiv))

        return JJ

    def _toy_problem(self, indiv):
        x = np.arange(-10, 10 + 0.1, 0.1)
        y = np.tanh(x**3 - x**2 - 1)
        artificial_noise = self._config.getint('EVALUATOR', 'artificialnoise')

        # In this test we have no noise by config file. But, if this were the
        # case, we would a have problem because the random of MATLAB is not
        # the random of Python :(
        # WORKAROUND: Generate the noise in matlab and process it in python

        # MAKE SOME NOISE!!!
        noise = \
            self._eng.eval('rand(length(zeros(1, ' + str(len(x)) + ')))-0.5')
        np_noise = np.array([s for s in noise[0]])
        y2 = y + np_noise * 500 * artificial_noise

        self._eng.workspace['indiv'] = indiv
        formal = self._eng.eval('indiv.formal').replace('S0', 'x')
        self._eng.workspace['x'] = self._eng.eval('-10:0.1:10')
        self._eng.workspace['formal'] = formal

        # Calculate J like the sum of the square difference of the
        # functions in every point

        lg.logger_.debug(formal)
        self._eng.workspace['y3'] = \
            self._eng.eval('zeros(1, ' + str(len(x)) + ')')
        self._eng.eval('eval([formal])')
        y3 = self._eng.eval('eval([formal])')

        # If the expression doesn't have the term 'x',
        # the eval returns a value (float) instead  of an array.
        # In that case transform it to an array
        try:
            np_y3 = np.array([s for s in y3[0]])
        except TypeError:
            np_y3 = np.repeat(y3, len(x))

        return np.sum((np_y3 - y2)**2)
