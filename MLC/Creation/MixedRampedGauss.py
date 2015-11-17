from BaseCreation import BaseCreation
import numpy as np
import math
import logging


class MixedRampedGauss(BaseCreation):
    def create(self, eng, config, gen_size):
        ramp = config.get_param('GP', 'ramp', type='arange')
        center = (np.max(ramp) + np.amin(ramp)) / 2
        sigma = config.getint('GP', 'gaussigma')
        samples = self.__create_gaussian_samples(ramp, center, sigma, gen_size)
        logging.getLogger('default').debug(
            '[MIXED_RAMP_GAUSS] Distribution generated: ' +
            np.array_str(samples))

    def __create_gaussian_samples(self, ramp, center, sigma, gen_size):
        pseudo_gaussian = np.power(math.e,
                                   (- (ramp - center) ** 2) / sigma ** 2)
        normalization = np.sum(pseudo_gaussian)
        gaussian = pseudo_gaussian / normalization * gen_size
        return np.round(np.cumsum(gaussian))


"""
            for j=1:length(n)-1;
                changed_param.maxdepthfirst=mlc_parameters.ramp(j);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(j)+round((n(j+1)-n(j))/2)),i,1,verb);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(j+1)),i,3,verb);
            end
"""
