# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import math
import MLC.Log.log as lg
import numpy as np

from BaseCreation import BaseCreation
from MLC.individual.Individual import Individual


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
            # Change th maxdepth propery while we generate the first generation
            Individual.set_maxdepthfirst(ramp[j])
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
