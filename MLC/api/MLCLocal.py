import argparse
import ConfigParser
import os
import shutil
import sys
import time

from MLC.api.Experiment import Experiment
from MLC.api.mlc import MLC
from MLC.api.mlc import ClosedExperimentException
from MLC.api.mlc import ExperimentNotExistException
from MLC.api.mlc import DuplicatedExperimentError
from MLC.api.mlc import InvalidExperimentException
from MLC.Application import Application
from MLC.config import get_templates_path
from MLC.config import set_working_directory
from MLC.db.mlc_repository import MLCRepository
from MLC.Log.log import get_gui_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation

logger = get_gui_logger()


class MLCLocal(MLC):
    DEFAULT_EXPERIMENT_CONFIG = os.path.join(get_templates_path(), "configuration.ini")

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

    def get_workspace_experiments(self):
        return self._experiments.keys()

    def get_experiment_configuration(self, experiment_name):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_configuration", experiment_name)

        return self._open_experiments[experiment_name].get_configuration()

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
        del self._open_experiments[experiment_name]

    def new_experiment(self, experiment_name, experiment_configuration=None):
        config = None
        if experiment_configuration is None:
            default_experiment_config = ConfigParser.ConfigParser()
            default_experiment_config.read(MLCLocal.DEFAULT_EXPERIMENT_CONFIG)
            config = Config.to_dictionary(default_experiment_config)
        else:
            config = experiment_configuration

        try:
            self._experiments[experiment_name] = Experiment.make(self._working_dir,
                                                                 experiment_name,
                                                                 config)
        except Exception, err:
            logger.error("Cannot create a new experiment. Error message: %s " % err)
            raise

    def delete_experiment(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        experiment_dir = os.path.join(self._working_dir, experiment_name)
        try:
            shutil.rmtree(experiment_dir)
            del self._experiments[experiment_name]
            if experiment_name in self._open_experiments:
                del self._open_experiments[experiment_name]
        except OSError:
            logger.info("[MLC_LOCAL] Error while trying to delete experiment file: {0}".format(file))

    def set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration_parameter", experiment_name)

        return MLC.set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value)

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

    def get_experiment_info(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        simulation = self._open_experiments[experiment_name].get_simulation()

        experiment_info = {
            "name": experiment_name,
            "generations": simulation.number_of_generations(),
            "individuals": MLCRepository.get_instance().count_individual(),
            "individuals_per_generation": Config.get_instance().getint("POPULATION", "size"),
            "filename": experiment_name + ".mlc"
        }

        return experiment_info

    def go(self, experiment_name, to_generation, from_generation=0, callbacks={}):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # load simulation
        experiment = self._open_experiments[experiment_name]
        simulation = experiment.get_simulation()

        # launch simulation
        app = Application(simulation, callbacks=callbacks)
        app.go(from_generation=from_generation, to_generation=to_generation)

        return True

    def get_individuals(self, experiment_name):
        """
        Return a list with IndividualData (see MLCRepository::IndividualData)
        :param experiment_name:
        :return:
        """
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # get simulation in order to load mlc experiment database
        simulation = self._open_experiments[experiment_name].get_simulation()

        # obtain individuals from the database
        individuals = MLCRepository.get_instance().get_individuals_data()
        return individuals

    def update_individual_cost(self, experiment_name, indiv_id, new_cost, new_ev_time, generation=-1):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        MLCRepository.get_instance().update_individual_cost(indiv_id, new_cost, new_ev_time, generation)

    def get_generation(self, experiment_name, generation_number):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # get simulation in order to load mlc experiment database
        simulation = self._open_experiments[experiment_name].get_simulation()

        return simulation.get_generation(generation_number)


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC API Test')

    parser.add_argument('-d', '--working-dir', default='.',
                        type=str, help='MLC working directory.')

    return parser.parse_args()
