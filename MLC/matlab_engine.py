import matlab.engine
import config as mlcv3_config
import os
import MLC.Log.log as lg
import random

class MatlabEngine:
    """
    Singleton class that allow to call matlab code from python using the
    matlab engine.
    """
    _engine_instance = None
    _rand_counter = 0
    _randoms = []

    @staticmethod
    def engine():
        if MatlabEngine._engine_instance is None:
            matlab_code_dir = mlcv3_config.get_matlab_path()

            # Check if a MATLAB session exists.
            try:
                sessions = matlab.engine.find_matlab()
                if len(sessions) > 0:
                    MatlabEngine._engine_instance = matlab.engine.connect_matlab(sessions[0])
                else:
                    MatlabEngine._engine_instance = matlab.engine.start_matlab()
            except AttributeError:
                # This version of MATLAB is not compatible with Shared sessions
                # Init the MATLAB engine in the regular way
                MatlabEngine._engine_instance = matlab.engine.start_matlab()

            MatlabEngine._engine_instance.addpath(matlab_code_dir)
            MatlabEngine._engine_instance.addpath(os.path.join(matlab_code_dir, "MLC_tools"))
            MatlabEngine._engine_instance.addpath(os.path.join(matlab_code_dir, "MLC_tools/Demo"))

        return MatlabEngine._engine_instance

    @staticmethod
    def rand():
        if MatlabEngine._engine_instance is None:
            raise UnboundLocalError('rand', 'Engine was not initialized')

        MatlabEngine._rand_counter += 1
        rand_value = None
        if not len(MatlabEngine._randoms):
            rand_value = random.random()
        else:
            try:
                rand_value = MatlabEngine._randoms.pop(0)
            except IndexError:
                lg.logger_.error("[MATLAB_ENGINE] Not enough random values. Aborting program.")
                raise

        # lg.logger_.debug("[ENGINE] Rand #%d - Value: %.6f" % (MatlabEngine._rand_counter, rand_value))
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

        if MatlabEngine._engine_instance is None:
            raise UnboundLocalError('rand', 'Engine was not initialized')
        MatlabEngine._rand_counter += n

        rand_list = []
        for _ in xrange(n):
            if not len(MatlabEngine._randoms):
                rand_list.append(random.random())
            else:
                rand_list.append(MatlabEngine._randoms.pop(0))

        indexes = [x[0] for x in sorted(enumerate(rand_list), key=lambda x:x[1])]
        return indexes


    @staticmethod
    def load_random_values(randoms_file):
        with open(randoms_file) as f:
            for line in f:
                MatlabEngine._randoms.append(float(line))

    @staticmethod
    def clear_random_values():
        MatlabEngine._randoms = []
