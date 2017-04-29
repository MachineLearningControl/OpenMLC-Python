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

import argparse
import cStringIO
import ConfigParser
import MLC.Common.util
import os
import shutil
import sys
import tarfile
import time

from collections import OrderedDict
from MLC.api.Experiment import Experiment
from MLC.api.mlc import MLC
from MLC.api.mlc import ClosedExperimentException
from MLC.api.mlc import ExperimentNotExistException
from MLC.api.mlc import DuplicatedExperimentError
from MLC.api.mlc import InvalidExperimentException
from MLC.api.mlc import EvaluationScriptNotExistException
from MLC.api.mlc import PreevaluationScriptNotExistException
from MLC.api.mlc import ImportExperimentPathNotExistException
from MLC.api.mlc import ConfigFilePathNotExistException
from MLC.Application import Application
from MLC.config import get_templates_path
from MLC.config import set_working_directory
from MLC.db.mlc_repository import MLCRepository
from MLC.Log.log import get_gui_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation
from MLC.arduino.protocol import ProtocolConfig
from MLC.arduino.connection.serialconnection import SerialConnectionConfig

logger = get_gui_logger()


class MLCLocal(MLC):
    DEFAULT_EXPERIMENT_CONFIG = os.path.join(get_templates_path(), "configuration.ini")
    DEFAULT_EVALUATION_SCRIPT = os.path.join(get_templates_path(), "toy_problem.py")
    DEFAULT_PREEVALUATION_SCRIPT = os.path.join(get_templates_path(), "default.py")

    def __init__(self, working_dir):
        if not os.path.exists(working_dir):
            raise Exception("Invalid working directory %s" % working_dir)

        # Set working dir for the MLC
        self._working_dir = working_dir
        set_working_directory(os.path.abspath(self._working_dir))

        self._experiments = {}
        self._open_experiments = {}
        logger.info("[MLC_LOCAL] [INIT] - Searching for experiments in {0}"
                    .format(self._working_dir))

        # Load the experiments found in the workspace
        subdirectories = next(os.walk(self._working_dir))[1]
        for experiment_name in subdirectories:
            experiment_dir = os.path.join(self._working_dir, experiment_name)

            try:
                self._experiments[experiment_name] = Experiment(experiment_dir, experiment_name)
                logger.info('[MLC_LOCAL] [INIT] - Found experiment in workspace: {0}'
                            .format(experiment_name))
            except InvalidExperimentException, err:
                logger.error("[MLC_LOCAL] [INIT] - Something go wrong loading experiment '{0}': {1}"
                             .format(experiment_name, err))
                pass
        logger.debug('[MLC_LOCAL] Experiments in the workspace: {0}'.format(len(self._experiments)))

    def get_working_dir(self):
        return self._working_dir

    def get_workspace_experiments(self):
        return self._experiments.keys()

    def get_experiment_configuration(self, experiment_name):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_configuration", experiment_name)

        return self._open_experiments[experiment_name].get_configuration()

    def reload_experiment_configuration(self, experiment_name):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_configuration", experiment_name)

        return self._open_experiments[experiment_name].reload_configuration()

    def set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration_parameter", experiment_name)

        return MLC.set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value)

    def set_experiment_configuration_from_file(self, experiment_name, config_filepath):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration_from_file", experiment_name)

        if not os.path.exists(config_filepath):
            raise ConfigFilePathNotExistException(config_filepath)

        experiment_config = ConfigParser.ConfigParser()
        experiment_config.read(config_filepath)
        new_config = Config.to_dictionary(experiment_config)
        # FIXME: Remove the db file from the config. Now the DB is a fixed part of the experiment
        new_config["BEHAVIOUR"]["savedir"] = experiment_name + ".db"
        self.set_experiment_configuration(experiment_name, new_config)

    def set_experiment_configuration(self, experiment_name, new_configuration):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration", experiment_name)

        # FIXME: Check the way the configuration rules are being coded
        # for section, params in new_configuration.iteritems():
        #     for param_name, param_value in new_configuration[section].iteritems():
        #         MLCConfigRules.get_instance().apply(section, param_name, param_value,
        #                                             self._open_experiments[experiment_name].get_simulation())

        experiment = self._open_experiments[experiment_name]
        configuration = experiment.get_configuration()

        # FIXME: Check the way the configuration rules are being coded
        # for section, params in new_configuration.iteritems():
        #     if not section in configuration:
        #         configuration[section] = {}
        #     for param_name, param_value in new_configuration[section].iteritems():
        #         configuration[section][param_name] = new_configuration[section][param_name]

        configuration.update(new_configuration)
        experiment.set_configuration(configuration)

    def open_experiment(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        # Add the project folder to the path to be able to use the Evaluation
        # and Preevaluation Scripts
        experiment_dir = os.path.join(self._working_dir, experiment_name)
        sys.path.append(experiment_dir)
        self._open_experiments[experiment_name] = self._experiments[experiment_name]

    def close_experiment(self, experiment_name):
        # Remove the project folder from the system path to avoid a module
        # problems between Evaluation and Preevaluation scripts from other projects
        experiment_dir = os.path.join(self._working_dir, experiment_name)
        sys.path.remove(experiment_dir)
        self._open_experiments[experiment_name].get_simulation().close()
        del self._open_experiments[experiment_name]

    def new_experiment(self, experiment_name,
                       experiment_configuration=None,
                       evaluation_script=None,
                       preevaluation_script=None):
        self._create_experiment_dir(experiment_name)

        config = experiment_configuration
        if experiment_configuration is None:
            config = MLCLocal.DEFAULT_EXPERIMENT_CONFIG

        self._load_new_experiment(experiment_name, 
                                  config,
                                  evaluation_script,
                                  preevaluation_script)

    def clone_experiment(self, experiment_name, cloned_experiment):
        source_path = os.path.join(self._working_dir, experiment_name)
        cloned_path = os.path.join(self._working_dir, cloned_experiment)

        # Copy the desired experiment and then change the config and db files names
        try:
            shutil.copytree(source_path, cloned_path)
            shutil.move(os.path.join(cloned_path, experiment_name + ".conf"),
                        os.path.join(cloned_path, cloned_experiment + ".conf"))

            shutil.move(os.path.join(cloned_path, experiment_name + ".db"),
                        os.path.join(cloned_path, cloned_experiment + ".db"))

            # Change the DB name inside the experiment
            experiment_config = ConfigParser.ConfigParser()
            experiment_config.read(os.path.join(cloned_path, cloned_experiment + ".conf"))
            experiment_config.set('BEHAVIOUR', 'savedir', cloned_experiment + ".db")
            with open(os.path.join(cloned_path, cloned_experiment + ".conf"), "w") as f:
                experiment_config.write(f)

            # Add the experiment to the list of experiments
            self._experiments[cloned_experiment] = Experiment(cloned_path, cloned_experiment)

        except Exception, err:
            logger.error("[MLC_LOCAL] [CLONE] - "
                         "An error ocurred while cloning project {0}. "
                         "Error {1}".format(experiment_name, err))

            # Try to remove the folder of the experiment created
            try:
                shutil.rmtree(cloned_path)
            except OSError:
                # If the directory does not exists, an exception is raised
                pass
            return False

        return True

    def rename_experiment(self, experiment_name_old, experiment_name_new):
        # Rename can be implemented as a clone and remove operation
        logger.info("[MLC_LOCAL] [RENAME] - Proceed to clone and remove the experiment given. "
                    "Old: {0} - New: {1}"
                    .format(experiment_name_old.encode('utf-8'), 
                            experiment_name_new.encode('utf-8')))
        if self.clone_experiment(experiment_name_old, experiment_name_new):
            try:
                self.delete_experiment(experiment_name_old)
            except OSError, err:
                # The experiment could not be removed
                logger.error("[MLC_LOCAL] [RENAME] - "
                             "Experiment {0} could not be deleted. Err: {1}"
                             .format(experiment_name_old, err))
                return False
            return True

        logger.error("[MLC_LOCAL] [RENAME] - "
                     "Experiment {0} could not be cloned. Aborting experiment rename."
                     .format(experiment_name_new))
        return False


    def delete_experiment(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        experiment_dir = os.path.join(self._working_dir, experiment_name)
        try:
            del self._experiments[experiment_name]
            if experiment_name in self._open_experiments:
                simulation = self._open_experiments[experiment_name].get_simulation().close()
                del self._open_experiments[experiment_name]

            shutil.rmtree(experiment_dir)
        except OSError:
            logger.info("[MLC_LOCAL] Error while trying to delete experiment file: {0}".format(file))
            raise

    def import_experiment(self, experiment_path):
        if not os.path.exists(experiment_path):
            raise ImportExperimentPathNotExistException(experiment_path)

        experiment_name = os.path.split(experiment_path)[1].split(".")[0]
        self._create_experiment_dir(experiment_name)

        try:
            with tarfile.open(experiment_path, "r:gz") as tar:
                tar.extractall(self._working_dir)
            logger.info("[MLC_LOCAL] Experiment {0} was succesfully imported.".format(experiment_name))
        except Exception, err:
            logger.error("[MLC_LOCAL] Experiment {0} could not be imported. Error msg: {1}"
                         .format(experiment_name, err))
            raise

        # Add the experiment to the list of experiments
        experiment_dir = os.path.join(self._working_dir, experiment_name)
        self._experiments[experiment_name] = Experiment(experiment_dir, experiment_name)

    def export_experiment(self, experiment_name):
        # Generate a tar file and store it in a variable, to be able to send
        # it via a websocket in the future
        c = cStringIO.StringIO()
        experiment_dir = os.path.join(self._working_dir, experiment_name)
        util.make_tarfile(experiment_dir, c)
        return c.getvalue()

    def get_experiment_info(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        simulation = self._open_experiments[experiment_name].get_simulation()

        experiment_info = OrderedDict()
        experiment_info["name"] = experiment_name
        experiment_info["generations"] = simulation.number_of_generations()
        experiment_info["individuals"] = MLCRepository.get_instance().count_individual()
        experiment_info["individuals_per_generation"] = Config.get_instance().getint("POPULATION", "size")

        if simulation.number_of_generations() != 0:
            # Get the best indiv description
            min_indiv_id = MLCRepository.get_instance().get_individual_with_min_cost_in_last_pop()
            min_indiv_data = MLCRepository.get_instance().get_individual_data(min_indiv_id)
            experiment_info["best_indiv_id"] = min_indiv_id
            experiment_info["best_indiv_value"] = min_indiv_data.get_value()
        return experiment_info

    def get_board_configuration(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        mlc_repo = MLCRepository.get_instance()

        boards = mlc_repo.get_board_configuration_ids()

        if len(boards) == 0:
            # creates default board configuration if not exists
            serial_connection = SerialConnectionConfig('/dev/ttyACM0')
            board_configuration = ProtocolConfig(serial_connection)

            # save default board configuration and serial connection
            board_id = mlc_repo.save_board_configuration(board_configuration)
            mlc_repo.save_serial_connection(serial_connection, board_id)

            return board_configuration, serial_connection
        else:
            # take first board configuration
            board_id = boards[0]

            # load board configuration and serial connection
            board_configuration = mlc_repo.load_board_configuration(board_id)
            serial_connection = mlc_repo.load_serial_connection(board_id)

            return board_configuration, serial_connection

    def save_board_configuration(self, experiment_name, board_configuration, connection):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        mlc_repo = MLCRepository.get_instance()

        boards = mlc_repo.get_board_configuration_ids()

        if len(boards) == 0:
            # save board configuration and serial connection
            board_id = mlc_repo.save_board_configuration(board_configuration)
            mlc_repo.save_serial_connection(connection, board_id)
        else:
            board_id = boards[0]
            mlc_repo.save_board_configuration(board_configuration, board_id=board_id)
            mlc_repo.save_serial_connection(connection, board_id=board_id, connection_id=board_id)

    def go(self, experiment_name, to_generation, from_generation=0, callbacks={}, gen_creator=None):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # load simulation
        experiment = self._open_experiments[experiment_name]
        simulation = experiment.get_simulation()

        # launch simulation
        app = Application(simulation, callbacks=callbacks, gen_creator=gen_creator)
        app.go(from_generation=from_generation, to_generation=to_generation)

        return True

    def get_individuals(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # get simulation in order to load mlc experiment database
        simulation = self._open_experiments[experiment_name].get_simulation()

        # obtain individuals from the database
        individuals = MLCRepository.get_instance().get_individuals_data()
        return individuals

    def get_generation(self, experiment_name, generation_number):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # get simulation in order to load mlc experiment database
        simulation = self._open_experiments[experiment_name].get_simulation()

        return simulation.get_generation(generation_number)

    def remove_generations_from(self, experiment_name, gen_number):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        MLCRepository.get_instance().remove_population_from(gen_number)
        MLCRepository.get_instance().remove_unused_individuals()

    def remove_generations_to(self, experiment_name, gen_number):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        MLCRepository.get_instance().remove_population_to(gen_number)
        MLCRepository.get_instance().remove_unused_individuals()

    def get_individual(self, experiment_name, individual_id):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # get simulation in order to load mlc experiment database
        simulation = self._open_experiments[experiment_name].get_simulation()

        # obtain individuals from the database
        individual = MLCRepository.get_instance().get_individual_data(individual_id)
        return individual

    def update_individual_cost(self, experiment_name, indiv_id, new_cost, new_ev_time, generation=-1):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        MLCRepository.get_instance().update_individual_cost(indiv_id, new_cost, new_ev_time, generation)

    def show_best(self, experiment_name, generation_number):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        experiment = self._open_experiments[experiment_name]
        simulation = experiment.get_simulation()

        app = Application(simulation)
        app.show_best(generation_number)

    def _create_experiment_dir(self, experiment_name):
        """
        If the experiment directory exists, raise an Exception
        """
        experiment_dir = os.path.join(self._working_dir, experiment_name)
        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)
        else:
            logger.error("[MLC_LOCAL] [CREATE_EXP_DIR] Could not add experiment {0}."
                         "Experiment already exists".format(experiment_name))
            raise DuplicatedExperimentError(experiment_name)

    def _load_new_experiment(self, experiment_name, config_path,
                             evaluation_script, preevaluation_script):
        experiment_config = ConfigParser.ConfigParser()
        experiment_config.read(config_path)
        config = Config.to_dictionary(experiment_config)

        if evaluation_script is None:
            evaluation_script = MLCLocal.DEFAULT_EVALUATION_SCRIPT

        if preevaluation_script is None:
            preevaluation_script = MLCLocal.DEFAULT_PREEVALUATION_SCRIPT

        if not os.path.exists(evaluation_script):
            raise EvaluationScriptNotExistException(experiment_name, evaluation_script)

        if not os.path.exists(preevaluation_script):
            raise PreevaluationScriptNotExistException(experiment_name, evaluation_script)

        try:
            self._experiments[experiment_name] = Experiment.make(self._working_dir,
                                                                 experiment_name,
                                                                 config,
                                                                 evaluation_script,
                                                                 preevaluation_script)
        except Exception, err:
            logger.error("Cannot create a new experiment. Error message: %s " % err)
            raise


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC API Test')

    parser.add_argument('-d', '--working-dir', default='.',
                        type=str, help='MLC working directory.')

    return parser.parse_args()
