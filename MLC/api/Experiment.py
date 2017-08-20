# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os
import argparse
import configparser
import MLC.config as path_solver
import shutil

from MLC.api.mlc import MLC
from MLC.api.mlc import ClosedExperimentException
from MLC.api.mlc import ExperimentNotExistException
from MLC.api.mlc import DuplicatedExperimentError
from MLC.api.mlc import InvalidExperimentException
from MLC.Application import Application
from MLC.db.mlc_repository import MLCRepository
from MLC.Log.log import get_gui_logger
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation

logger = get_gui_logger()


class Experiment:
    # FIXME: one simulation at a time
    __last_simulation = None

    def __init__(self, working_dir, experiment_name):
        logger.info("[EXPERIMENT {0}] Proceed to load {1} experiment"
                    .format(experiment_name, os.path.join(working_dir)))
        Experiment.check_configuration(working_dir, experiment_name)
        cfg, db = Experiment.get_experiment_files(working_dir, experiment_name)
        self._name = experiment_name
        self._config_file = cfg
        self._db_file = db
        self._simulation = None

        self._configuration = configparser.ConfigParser()
        self._configuration.read(self._config_file)

    def get_simulation(self):
        if Experiment.__last_simulation is None or Experiment.__last_simulation != self._simulation:
            MLCRepository._instance = None
            Config._instance = None
            Config.get_instance().read(self._config_file)
            set_logger(Config.get_instance().get('LOGGING', 'logmode'))

            if Experiment.__last_simulation:
                Experiment.__last_simulation.close()

            self._simulation = Simulation(self._name)
            Experiment.__last_simulation = self._simulation

        return self._simulation

    def get_configuration(self):
        return Config.to_dictionary(self._configuration)

    def reload_configuration(self):
        """
        Load again the experiment configuration, reading the config file from disk
        """
        self._configuration = ConfigParser.ConfigParser()
        self._configuration.read(self._config_file)
        Config.get_instance().read(self._config_file)
        return Config.to_dictionary(self._configuration)

    def set_configuration(self, new_configuration):
        self._configuration = Config.from_dictionary(new_configuration, config_type=ConfigParser.ConfigParser)
        self._configuration.write(open(self._config_file, "wt"))

        # Reload the configuration
        Config.get_instance().read(self._config_file)

    @staticmethod
    def make(working_dir, experiment_name, experiment_configuration,
             evaluation_script, preevaluation_script):
        # Obtain experiment filenames
        experiment_dir = os.path.join(working_dir, experiment_name)
        experiment_cf, experiment_db = Experiment.get_experiment_files(experiment_dir, experiment_name)

        # Put DB parameters in the configuration file
        if "BEHAVIOUR" not in experiment_configuration:
            experiment_configuration["BEHAVIOUR"] = {}

        experiment_configuration["BEHAVIOUR"]["save"] = "true"
        # FIXME: Remove this parameter. It is no longer necessary
        experiment_configuration["BEHAVIOUR"]["savedir"] = experiment_name + ".db"
        new_configuration = Config.from_dictionary(experiment_configuration)

        # Save experiment configuration file
        new_configuration.write(open(experiment_cf, "wt"))

        # Create an empty simulation in order to create the experiment database
        Config._instance = None
        Config.get_instance().read(experiment_cf)
        simulation = Simulation(experiment_name)

        def folder_structure_creator(folder_to_create, file_to_copy):
            folder_path = os.path.join(experiment_dir, folder_to_create)
            os.makedirs(folder_path)
            shutil.copy(file_to_copy, folder_path)
            init_file = os.path.join(folder_path, "__init__.py")
            open(init_file, "w").close()

        folder_structure_creator("Evaluation", evaluation_script)
        folder_structure_creator("Preevaluation", preevaluation_script)

        # Load experiment
        try:
            return Experiment(experiment_dir, experiment_name)
        except Exception as err:
            logger.error("Cannot create a new experiment. Error message: %s " % err)
            raise

    @staticmethod
    def get_experiment_files(working_dir, experiment_name):
        experiment_db_name = experiment_name + ".db"
        experiment_cf_name = experiment_name + ".conf"

        experiment_db = os.path.join(working_dir, experiment_db_name)
        experiment_cf = os.path.join(working_dir, experiment_cf_name)
        return experiment_cf, experiment_db

    @staticmethod
    def check_configuration(working_dir, experiment_name):
        if not os.path.exists(working_dir):
            raise InvalidExperimentException("Invalid working directory %s" % working_dir)

        experiment_db_name = experiment_name + ".db"
        experiment_cf_name = experiment_name + ".conf"

        experiment_db = os.path.join(working_dir, experiment_db_name)
        experiment_cf = os.path.join(working_dir, experiment_cf_name)

        if not os.path.exists(experiment_db):
            raise InvalidExperimentException("Database file does not exist %s" % experiment_db)

        if not os.path.exists(experiment_cf):
            raise InvalidExperimentException("Configuration file does not exist %s" % experiment_cf)

        # TODO: Validate that the configuration database its ok
        try:
            import configparser
            config = configparser.ConfigParser()
            config.readfp(open(experiment_cf))

            if not config.getboolean("BEHAVIOUR", "save"):
                raise InvalidExperimentException("BEHAVIOUR::save configured as false in %s, must be true" % experiment_cf)

            conf_db = config.get("BEHAVIOUR", "savedir")
            if conf_db != experiment_db_name:
                raise InvalidExperimentException("Invalid DB name configured in %s: is '%s' and should be '%s'" %
                                                 (experiment_cf, conf_db, experiment_db_name))

            return Config.to_dictionary(config), experiment_db

            # TODO: We need to check for the existence of a Evaluation and Preevaluation folder. If so, we have to also
            # check if the variable in the configuration matches the file in this folders?

        except Exception as err:
            raise InvalidExperimentException("Error reading configuration file %s: %s" % (experiment_cf, err))
