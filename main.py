#!/usr/bin/python2.7
import numpy as np
from MLC.Application import Application
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.matlab_engine import MatlabEngine


def initialize_config():
    config = Config.get_instance()
    config.read('conf/configuration.ini')
    return config


def main():
    np.set_printoptions(precision=4, suppress=True)
    eng = MatlabEngine.engine()
    config = initialize_config()
    eng.rand('seed', 20.0, nargout=0)

    # Create the MLC2 object and store it in the workspace. With this
    # feature we will be able to call every function of the MATLAB code
    # from any part of the code where the engine is available
    eng.workspace['wmlc'] = eng.MLC2()

    mlc = Application(config.get('LOGGING', 'logmode'))
    mlc.go(3, 2)
    raw_input("Press enter to continue...")

if __name__ == "__main__":
    main()
