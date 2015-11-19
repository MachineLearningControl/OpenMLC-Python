from BaseCreation import BaseCreation
import numpy as np
import math
import logging


class MixedRampedGauss(BaseCreation):
    def __init__(self, eng, config):
        BaseCreation.__init__(self, eng, config)

    def create(self, gen_size):
        ramp = self._config.get_param('GP', 'ramp', type='arange')
        center = (np.max(ramp) + np.amin(ramp)) / 2
        sigma = self._config.getint('GP', 'gaussigma')
        distribution = self.__create_gaussian_distribution(ramp, center,
                                                           sigma, gen_size)
        logging.getLogger('default').debug(
            '[MIXED_RAMP_GAUSS] Distribution generated: ' +
            np.array_str(distribution))

        index = 0
        while index < len(distribution) - 1:
            aux = round((distribution(index+1) - distribution(index)) / 2)
            indiv_indexes_1 = np.arange(1, aux)
            indiv_indexes_2 = np.arange(1, distribution(index+1))

            self._fill_creation(indiv_indexes_1, index, 1)
            self._fill_creation(indiv_indexes_2, index, 3)
            ++index


    def __create_gaussian_distribution(self, ramp, center, sigma, gen_size):
        pseudo_gaussian = np.power(math.e,
                                   (- (ramp - center) ** 2) / sigma ** 2)
        normalization = np.sum(pseudo_gaussian)
        gaussian = pseudo_gaussian / normalization * gen_size
        return np.round(np.cumsum(gaussian))
