#!/usr/bin/python2.7
import matlab.engine
from MLC.Application import Application
from MLC.Config.Config import Config


def set_path(eng):
    eng.addpath("./matlab_code")
    eng.addpath("./matlab_code/MLC_tools")
    eng.addpath("./matlab_code/MLC_tools/Demo")


def initialize_matlab():
    eng = matlab.engine.start_matlab()
    return eng


def initialize_config():
    config = Config()
    config.read('conf/configuration.ini')
    return config


def main():
    eng = initialize_matlab()
    config = initialize_config()
    set_path(eng)
    eng.rand('seed', 20.0, nargout=0)

    # Create the MLC2 object and store it in the workspace. With this
    # feature we will be able to call every function of the MATLAB code
    # from any part of the code where the engine is available
    eng.workspace['wmlc'] = eng.MLC2()

    mlc = Application(eng, config)
    mlc.go(3, 2)

if __name__ == "__main__":
    main()
