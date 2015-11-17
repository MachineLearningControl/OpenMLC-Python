#!/usr/bin/python2.7
import matlab.engine
from MLC.Population import Population
from MLC.Config.Config import Config
import logging
import logging.config

def set_path(eng):
    eng.addpath("./matlab_code")
    eng.addpath("./matlab_code/MLC_tools")
    eng.addpath("./matlab_code/MLC_tools/Demo")


def initialize_matlab():
    eng = matlab.engine.start_matlab()
    return eng


def initialize_config():
    config = Config()
    config.read('configuration.ini')
    return config


def init_logger():
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("default")


def main():
    eng = initialize_matlab()
    config = initialize_config()
    init_logger()
    set_path(eng)

    pop = Population(eng, config, 1)
    pop.create()
    raw_input("Press Enter to continue...")


if __name__ == "__main__":
    main()
