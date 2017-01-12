import os
import argparse
import ConfigParser

from MLC.api.mlc import MLC
from MLC.api.mlc import ClosedExperimentException
from MLC.api.mlc import ExperimentNotExistException
from MLC.api.mlc import DuplicatedExperimentError
from MLC.Application import Application
from MLC.config import set_working_directory
from MLC.db.mlc_repository import MLCRepository
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation

class Experiment:
    # FIXME: one simulation at a time
    __last_simulation = None

    def __init__(self, working_dir, experiment_name):
        Experiment.check_configuration(working_dir, experiment_name)
        cfg, db = Experiment.get_experiment_files(working_dir, experiment_name)
        self._name = experiment_name
        self._config_file = cfg
        self._db_file = db
        self._simulation = None

        self._configuration = ConfigParser.ConfigParser()
        self._configuration.read(self._config_file)

    def get_simulation(self):
        if Experiment.__last_simulation is None or Experiment.__last_simulation != self._simulation:
            MLCRepository._instance = None
            Config._instance = None
            Config.get_instance().read(self._config_file)
            set_logger(Config.get_instance().get('LOGGING', 'logmode'))

            self._simulation = Simulation()
            Experiment.__last_simulation = self._simulation

        return self._simulation

    def get_configuration(self):
        return Config.to_dictionary(self._configuration)

    def set_configuration(self, new_configuration):
        self._configuration = Config.from_dictionary(new_configuration, config_type=ConfigParser.ConfigParser)
        self._configuration.write(open(self._config_file, "wt"))

        # Reload the configuration
        Config.get_instance().read(self._config_file)

    @staticmethod
    def get_experiment_files(working_dir, experiment_name):
        experiment_db_name = experiment_name + ".mlc"
        experiment_cf_name = experiment_name + ".conf"

        experiment_db = os.path.join(working_dir, experiment_db_name)
        experiment_cf = os.path.join(working_dir, experiment_cf_name)
        return experiment_cf, experiment_db

    @staticmethod
    def check_configuration(working_dir, experiment_name):
        if not os.path.exists(working_dir):
            raise InvalidExperimentException("Invalid working directory %s" % working_dir)

        experiment_db_name = experiment_name + ".mlc"
        experiment_cf_name = experiment_name + ".conf"

        experiment_db = os.path.join(working_dir, experiment_db_name)
        experiment_cf = os.path.join(working_dir, experiment_cf_name)

        if not os.path.exists(experiment_db):
            raise InvalidExperimentException("Database file does not exist %s" % experiment_db)

        if not os.path.exists(experiment_cf):
            raise InvalidExperimentException("Configuration file does not exist %s" % experiment_cf)

        # TODO: Validate that the configuration database its ok
        try:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.readfp(open(experiment_cf))

            if not config.getboolean("BEHAVIOUR", "save"):
                raise InvalidExperimentException("BEHAVIOUR::save configured as false in %s, must be true" % experiment_cf)

            conf_db = config.get("BEHAVIOUR", "savedir")
            if conf_db != experiment_db_name:
                raise InvalidExperimentException("Invalid DB name configured in %s: is '%s' and should be '%s'" %
                                                 (experiment_cf, conf_db, experiment_db_name))

            return Config.to_dictionary(config), experiment_db

        except Exception, err:
            raise InvalidExperimentException("Error reading configuration file %s: %s" % (experiment_cf, err))
