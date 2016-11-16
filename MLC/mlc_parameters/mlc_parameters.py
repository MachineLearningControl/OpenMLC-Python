import ConfigParser
import numpy as np
import MLC.Log.log as lg


class saved():

    def __init__(self, cr):
        self.cr = cr

    def __enter__(self):
        self.cr.save()
        return self.cr

    def __exit__(self, type, value, traceback):
        self.cr.restore()


class Config(ConfigParser.ConfigParser):
    """
    Singleton class that parse and manipulates the Config file of the MLC
    """
    _instance = None

    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        self._log_prefix = '[CONFIG] '

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

    def save(self):
        self._dictionary = Config.to_dictionary(self)

    def restore(self):
        for section, options in self._dictionary.iteritems():
            for opt, value in options.iteritems():
                self.set(section, opt, value)

    @staticmethod
    def to_dictionary(config_parser):
        config_dict = {}
        for section in config_parser.sections():
            config_dict[section] = {}
            for option in config_parser.options(section):
                config_dict[section][option] = config_parser.get(section, option)
        return config_dict

    @classmethod
    def from_dictionary(cls, config_dict, config_type=None):
        config = cls() if config_type is None else config_type()
        for section, options in config_dict.iteritems():
            config.add_section(section)
            for opt, value in options.iteritems():
                config.set(section, opt, value)
        return config