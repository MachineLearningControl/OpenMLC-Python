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

import os
import MLC.Log.log as lg
import random


class RandomManager:
    """
    Singleton class that manage the way in which the random numbers are generated.
    The options available at the moment are:
    * Load MATLAB generated randoms from a fike
    * Use Python randoms
    """
    _rand_counter = 0
    _randoms = []

    @staticmethod
    def rand():
        RandomManager._rand_counter += 1
        rand_value = None
        if not len(RandomManager._randoms):
            rand_value = random.random()
        else:
            try:
                rand_value = RandomManager._randoms.pop(0)
            except IndexError:
                lg.logger_.error("[RANDOM_MANAGER] Not enough random values. Aborting program.")
                raise

        # lg.logger_.debug("[RANDOM_MANAGER] Rand #%d - Value: %.6f" % (RandomManager._rand_counter, rand_value))
        return rand_value

    @staticmethod
    def randperm(n):
        """
        This function throws as many rands as the value of n and return a
        list of the indexes of the ordered array of randoms.
        Example:
        If n == 5 and the randoms gathered are:
        0.1 0.9 0.2 0.6 0.3
        1   2   3   4   5
        The list returned by the method will be:
        0.1 0.2 0.3 0.6 0.9
        1   3   5   4   2
        [1,3,5,4,2]
        """
        RandomManager._rand_counter += n
        rand_list = []

        for _ in xrange(n):
            if not len(RandomManager._randoms):
                rand_list.append(random.random())
            else:
                rand_list.append(RandomManager._randoms.pop(0))

        indexes = [x[0] for x in sorted(enumerate(rand_list), key=lambda x:x[1])]
        return indexes

    @staticmethod
    def load_random_values(randoms_file):
        with open(randoms_file) as f:
            for line in f:
                RandomManager._randoms.append(float(line))

    @staticmethod
    def clear_random_values():
        RandomManager._randoms = []
