import numpy as np
import MLC.Log.log as lg
import matplotlib.pyplot as plt

from MLC.matlab_engine import MatlabEngine
from MLC.mlc_parameters.mlc_parameters import Config


def individual_data(indiv):
    np.set_printoptions(precision=4, suppress=True)
    x = np.arange(-10, 10 + 0.1, 0.1)
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
    formal = indiv.get_formal().replace('S0', 'x')
    eng.workspace['x'] = eng.eval('-10:0.1:10')
    eng.workspace['formal'] = formal

    # Calculate J like the sum of the square difference of the
    # functions in every point

    lg.logger_.debug('[POP][TOY_PROBLEM] Individual Formal: ' + formal)
    eng.workspace['y3'] = eng.eval('zeros(1, ' + str(len(x)) + ')')
    eng.eval('eval([formal])')
    y3 = eng.eval('eval([formal])')

    # If the expression doesn't have the term 'x',
    # the eval returns a value (float) instead  of an array.
    # In that case transform it to an array
    try:
        np_y3 = np.array([s for s in y3[0]])
    except TypeError:
        np_y3 = np.repeat(y3, len(x))

    return x, y, y2, np_y3,


def cost(indiv):
    x, y, y2, np_y3 = individual_data(indiv)
    return float(np.sum((np_y3 - y2)**2))


def show_best(index, indiv, block=True):
    x, y, y2, np_y3 = individual_data(indiv)
    # FIXME: Absolute only makes sense if we're working with complex numbers. It's not the case...
    y4 = np.sqrt((y - np_y3)**2 / (1 + np.absolute(x**2)))

    plt.clf()
    plt.suptitle("Individual N#{0} - Cost: {1}".format(index, indiv.get_cost()))
    plt.subplot(2, 1, 1)
    plt.plot(x, y, x, y2, '*', x, np_y3)

    plt.subplot(2, 1, 2)
    plt.plot(x, y4, '*r')
    plt.yscale('log')
    plt.show(block=block)


def dummy_test():
    x = np.arange(-10, 10, 0.1)
    y = np.tanh(x**3 - x**2 - 1)

    y2 = y

    y3 = [-0.9799, -0.9796, -0.9793, -0.9791, -0.9788, -0.9785, -0.9783, -0.9780, -0.9777, -0.9774, -0.9771, -0.9768,
          -0.9765, -0.9761, -0.9758, -0.9755, -0.9751, -0.9747, -0.9744, -0.9740, -0.9736, -0.9732, -0.9728, -0.9724,
          -0.9719, -0.9715, -0.9710, -0.9706, -0.9701, -0.9696, -0.9691, -0.9685, -0.9680, -0.9674, -0.9669, -0.9663,
          -0.9657, -0.9650, -0.9644, -0.9637, -0.9630, -0.9623, -0.9615, -0.9608, -0.9600, -0.9591, -0.9583, -0.9574,
          -0.9565, -0.9555, -0.9545, -0.9535, -0.9524, -0.9513, -0.9502, -0.9489, -0.9477, -0.9464, -0.9450, -0.9435,
          -0.9420, -0.9405, -0.9388, -0.9371, -0.9353, -0.9334, -0.9313, -0.9292, -0.9270, -0.9246, -0.9222, -0.9195,
          -0.9167, -0.9138, -0.9106, -0.9072, -0.9037, -0.8998, -0.8958, -0.8914, -0.8866, -0.8816, -0.8761, -0.8701,
          -0.8637, -0.8567, -0.8490, -0.8406, -0.8314, -0.8212, -0.8100, -0.7974, -0.7834, -0.7677, -0.7499, -0.7296,
          -0.7064, -0.6797, -0.6485, -0.6119, 0, 0.5162, 0.4527, 0.3743, 0.2760, 0.1508, -0.0111, -0.2222, -0.4947,
          -0.8187, -0.9336, -0.6120, -0.3164, -0.0834, 0.0953, 0.2329, 0.3403, 0.4254, 0.4940, 0.5501, 0.5966, 0.6355,
          0.6686, 0.6969, 0.7213, 0.7426, 0.7613, 0.7778, 0.7924, 0.8055, 0.8172, 0.8277, 0.8373, 0.8460, 0.8539,
          0.8611, 0.8678, 0.8739, 0.8796, 0.8848, 0.8896, 0.8942, 0.8984, 0.9023, 0.9059, 0.9094, 0.9126, 0.9156,
          0.9185, 0.9212, 0.9237, 0.9261, 0.9284, 0.9306, 0.9326, 0.9346, 0.9364, 0.9382, 0.9399, 0.9415, 0.9430,
          0.9445, 0.9459, 0.9472, 0.9485, 0.9497, 0.9509, 0.9520, 0.9531, 0.9542, 0.9552, 0.9561, 0.9571, 0.9580,
          0.9588, 0.9597, 0.9605, 0.9613, 0.9620, 0.9627, 0.9634, 0.9641, 0.9648, 0.9654, 0.9660, 0.9666, 0.9672,
          0.9678, 0.9683, 0.9689, 0.9694, 0.9699, 0.9704, 0.9709, 0.9713, 0.9718, 0.9722, 0.9726, 0.9730, 0.9735]

    y4 = np.sqrt((y - y3)**2 / (1 + np.absolute(x**2)))

    plt.subplot(2, 1, 1)
    plt.plot(x, y, x, y2, '*', x, y3)

    plt.subplot(2, 1, 2)
    plt.plot(x, y4, '*r')
    plt.yscale('log')
    plt.show()
