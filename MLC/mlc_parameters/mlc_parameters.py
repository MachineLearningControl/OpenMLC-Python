import ConfigParser
import numpy as np
import MLC.Log.log as lg
from MLC.matlab_engine import MatlabEngine


class Config(ConfigParser.ConfigParser):
    """
    Singleton class that parse and manipulates the Config file of the MLC
    """
    _instance = None

    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        self._log_prefix = '[CONFIG] '

    def get_matlab_object(self):
        return MatlabEngine.engine().eval('wmlc.parameters')

    def get_list(self, section, param, item_type=int):
        value = self.get(section, param)

        split_range = value.split(":")
        if len(split_range) == 2:
            return [item_type(x) for x in range(int(split_range[0]), int(split_range[1]))]

        split_list = value.split(",")
        return [item_type(x) for x in split_list]

    @staticmethod
    def get_instance():
        if Config._instance is None:
            Config._instance = Config()

        return Config._instance
