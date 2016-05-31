import matlab.engine

class MatlabEngine:
    """
    Singleton class that allow to call matlab code from python using the matlab engine.
    """
    _engine_instance = None

    @staticmethod
    def engine():
        if MatlabEngine._engine_instance is None:
            MatlabEngine._engine_instance = matlab.engine.start_matlab()
            MatlabEngine._engine_instance.addpath("./../matlab_code")
            MatlabEngine._engine_instance.addpath("./../matlab_code/MLC_tools")
            MatlabEngine._engine_instance.addpath("./../matlab_code/MLC_tools/Demo")

        return MatlabEngine._engine_instance