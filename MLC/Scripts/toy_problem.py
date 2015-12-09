import numpy as np
import MLC.Log.log as lg


def toy_problem(eng, config, indiv):
    np.set_printoptions(precision=4, suppress=True)
    x = np.arange(-10, 10 + 0.1, 0.1)
    y = np.tanh(x**3 - x**2 - 1)
    # artificial_noise = self._config.getint('EVALUATOR', 'artificialnoise')

    # In this test we have no noise by config file. But, if this were the
    # case, we would a have problem because the random of MATLAB is not
    # the random of Python :(
    # WORKAROUND: Generate the noise in matlab and process it in python

    # MAKE SOME NOISE!!!
    # noise = \
    #     eng.eval('rand(length(zeros(1, ' + str(len(x)) + ')))-0.5')
    # np_noise = np.array([s for s in noise[0]])
    # y2 = y + np_noise * 500 * artificial_noise
    y2 = y

    eng.workspace['indiv'] = indiv
    formal = eng.eval('indiv.formal').replace('S0', 'x')
    eng.workspace['x'] = eng.eval('-10:0.1:10')
    eng.workspace['formal'] = formal

    # Calculate J like the sum of the square difference of the
    # functions in every point

    lg.logger_.debug('[POP][TOY_PROBLEM] Individual Formal: ' + formal)
    eng.workspace['y3'] = \
        eng.eval('zeros(1, ' + str(len(x)) + ')')
    eng.eval('eval([formal])')
    y3 = eng.eval('eval([formal])')

    # If the expression doesn't have the term 'x',
    # the eval returns a value (float) instead  of an array.
    # In that case transform it to an array
    try:
        np_y3 = np.array([s for s in y3[0]])
    except TypeError:
        np_y3 = np.repeat(y3, len(x))

    return np.sum((np_y3 - y2)**2)