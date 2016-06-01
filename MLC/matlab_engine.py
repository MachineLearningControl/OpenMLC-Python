import matlab.engine
import config as mlcv3_config
import os

class MatlabEngine:
    """
    Singleton class that allow to call matlab code from python using the matlab engine.
    """
    _engine_instance = None

    @staticmethod
    def engine():
        if MatlabEngine._engine_instance is None:
            matlab_code_dir = mlcv3_config.get_matlab_path()
            MatlabEngine._engine_instance = matlab.engine.start_matlab()
            MatlabEngine._engine_instance.addpath(matlab_code_dir)
            MatlabEngine._engine_instance.addpath(os.path.join(matlab_code_dir, "MLC_tools"))
            MatlabEngine._engine_instance.addpath(os.path.join(matlab_code_dir, "MLC_tools/Demo"))

        return MatlabEngine._engine_instance