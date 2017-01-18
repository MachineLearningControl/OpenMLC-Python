import numpy as np
import MLC.Log.log as lg
import matplotlib.pyplot as plt
import sys

from MLC.matlab_engine import MatlabEngine
from MLC.mlc_parameters.mlc_parameters import Config


def individual_data(indiv):
    x = np.linspace(-10.0, 10.0, num=201)
    y = np.tanh(x**3 - x**2 - 1)

    eng = MatlabEngine.engine()
    config = Config.get_instance()
    # artificial_noise = self._config.getint('EVALUATOR', 'artificialnoise')

    # In this test we have no noise by config file. But, if this were the
    # case, we would a have problem because the random of MATLAB is not
    # the random of Python :(
    # WORKAROUND: Generate the noise in matlab and process it in python

    # MAKE SOME NOISE!!!
    # noise = eng.eval('rand(length(zeros(1, ' + str(len(x)) + ')))-0.5')
    # np_noise = np.array([s for s in noise[0]])
    # y2 = y + np_noise * 500 * artificial_noise

    y2 = y

    if isinstance(indiv.get_formal(), str):
        formal = indiv.get_formal().replace('S0', 'x')
    else:
        # toy problem support for multiple controls
        formal = indiv.get_formal()[0].replace('S0', 'x')

    eng.workspace['x'] = eng.eval('-10:0.1:10')
    eng.workspace['formal'] = formal

    # Calculate J like the sum of the square difference of the
    # functions in every point

    lg.logger_.debug('[POP][TOY_PROBLEM] Individual Formal: ' + formal)
    eng.workspace['y3'] = eng.eval('zeros(1, ' + str(len(x)) + ')')
    eng.eval('eval([formal])')
    y3 = eng.eval('eval([formal])')

    try:
        np_y3 = np.array([s for s in y3[0]])
    except TypeError:
        np_y3 = np.repeat(y3, len(x))

    return x, y, y2, np_y3


def cost(indiv):
    x, y, y2, mlc_y3 = individual_data(indiv)
    cost_mlc_y3 = None
    try:
        cost_mlc_y3 = float(np.sum((mlc_y3 - y2)**2))
    except FloatingPointError, err:
        np.seterr(all='ignore')
        cost_mlc_y3 = float(np.sum((mlc_y3 - y2)**2))
        np.seterr(all='raise')
    return cost_mlc_y3


def show_best(index, generation, indiv, cost, block=True):
    x, y, y2, mlc_y3 = individual_data(indiv)
    # FIXME: Absolute only makes sense if we're working with complex numbers. It's not the case...
    y4 = np.sqrt((y - mlc_y3)**2 / (1 + np.absolute(x**2)))

    fig = plt.figure()
    # Put figure window on top of all other windows
    fig.canvas.manager.window.setWindowModality(Qt.ApplicationModal)

    plt.suptitle("Generation N#{0} - Individual N#{1}\n"
                 "Cost: {1}\n Formal: {3}".format(generation,
                                                  index,
                                                  cost,
                                                  indiv.get_formal()))
    plt.subplot(2, 1, 1)
    plt.plot(x, y, x, y2, '*', x, mlc_y3)

    plt.subplot(2, 1, 2)
    plt.plot(x, y4, '*r')
    plt.yscale('log')
    plt.show(block=block)
