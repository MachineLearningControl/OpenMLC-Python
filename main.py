#!/usr/bin/python2.7
import numpy as np
import importlib
from MLC.Application import Application
from MLC.Common.RandomManager import RandomManager
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation
from MLC.Log.log import set_logger


def initialize_config():
    config = Config.get_instance()
    config.read('conf/configuration.ini')
    return config


def main():
    # Set printable resolution (don't alter numpy interval resolution)
    np.set_printoptions(precision=9)
    # Show full arrays, no matter what size do they have
    np.set_printoptions(threshold=np.inf)
    # Don't show scientific notation
    np.set_printoptions(suppress=True)

    # MATLAB random numbers, used in integration tests
    RandomManager.load_random_values("./tests/integration_tests/matlab_randoms.txt")

    # load configuration
    config = initialize_config()

    # set logger
    log_mode = config.get('LOGGING', 'logmode')
    set_logger(log_mode)

    simulation = Simulation()
    mlc = Application(simulation, log_mode)
    mlc.go(3, fig=True)
    raw_input("Press enter to continue...")

if __name__ == "__main__":
    main()
