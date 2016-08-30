import math
import MLC.Log.log as lg
import numpy as np

from BaseCreation import BaseCreation


class MixedRampedGauss(BaseCreation):

    def __init__(self):
        BaseCreation.__init__(self)

    def create(self, gen_size):
        ramp = np.array(self._config.get_list('GP', 'ramp'), dtype='float')
        center = (np.max(ramp) + np.amin(ramp)) / 2
        sigma = self._config.getint('GP', 'gaussigma')
        distrib = self.__create_gaussian_distribution(ramp, center,
                                                      sigma, gen_size)

        # Append a zero to the begginning of the array
        distrib = np.concatenate((np.array([0.]), distrib))
        lg.logger_.debug('[MIXED_RAMP_GAUSS] Distribution generated: ' +
                         np.array_str(distrib))

        i = 0
        j = 0
        while j < len(distrib) - 1:
            # REMOVE: MATLAB_COMPAT_ONLY
            param = self._eng.eval('wmlc.parameters')
            self._eng.set_maxdepthfirst(param, float(ramp[j]))

            aux = distrib[j] + round((distrib[j + 1] - distrib[j]) / 2)

            # Numpy ranges doesn't include the last element as in python.
            # Increment the max value by 1 to correct this effect
            indiv_indexes_1 = np.arange(1, aux + 1, dtype=int)
            indiv_indexes_2 = np.arange(1, distrib[j + 1] + 1, dtype=int)

            i = self._fill_creation(indiv_indexes_1, i, 1)
            i = self._fill_creation(indiv_indexes_2, i, 3)
            j += 1

    def __create_gaussian_distribution(self, ramp, center, sigma, gen_size):
        lg.logger_.debug('[MIXED_RAMP_GAUSS] Ramp: ' + np.array_str(ramp) +
                         ' - Center: ' + str(center) + ' Sigma: ' + str(sigma))

        pseudo_gaussian = np.power(math.e, (- (ramp - center) ** 2) / sigma ** 2) * gen_size
        lg.logger_.debug('[MIXED_RAMP_GAUSS] Gaussian: ' + np.array_str(pseudo_gaussian))

        normalization = np.sum(pseudo_gaussian)
        gaussian = pseudo_gaussian / normalization * gen_size
        return np.round(np.cumsum(gaussian))
