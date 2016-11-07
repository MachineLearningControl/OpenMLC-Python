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
