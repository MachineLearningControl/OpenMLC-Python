import matlab.engine
import config as mlcv3_config
import os
import MLC.Log.log as lg


class MatlabEngine:
    """
    Singleton class that allow to call matlab code from python using the
    matlab engine.
    """
    _engine_instance = None
    _rand_counter = 0

    @staticmethod
    def engine():
        if MatlabEngine._engine_instance is None:
            matlab_code_dir = mlcv3_config.get_matlab_path()

            # Check if a MATLAB session exists.
            try:
                sessions = matlab.engine.find_matlab()
                if len(sessions) > 0:
                    MatlabEngine._engine_instance = matlab.engine.connect_matlab(sessions[0])
                    print "Using Shared Session {}".format(sessions[0])
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

        rand_value = MatlabEngine._engine_instance.rand()
        MatlabEngine._rand_counter += 1
        # lg.logger_.debug("[ENGINE] Rand #%d - Value: %f" % (MatlabEngine._rand_counter, rand_value))
        return rand_value
