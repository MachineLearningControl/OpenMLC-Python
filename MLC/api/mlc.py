import os
import argparse
import ConfigParser

from MLC.Application import Application
from MLC.config import set_working_directory
from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation


class MLCException(Exception):
    pass


class ClosedExperimentException(MLCException):

    def __init__(self, experiment_name, operation_name):
        MLCException.__init__(self, "Cannot execute operation %s because '%s' is closed." % (experiment_name, operation_name))


class ExperimentNotExistException(MLCException):

    def __init__(self, experiment_name):
        MLCException.__init__(self, "Experiment '%s' does not exist." % experiment_name)


class DuplicatedExperimentError(MLCException):

    def __init__(self, experiment_name):
        MLCException.__init__(self, "Experiment '%s' already exists." % experiment_name)


class MLC:

    def open_experiment(self, experiment_name):
        """
            Open experiment in the workspace.
            :param experiment_name:
            :return:
        """
        raise NotImplementedError("MLC::open_experiment not implemented")

    def close_experiment(self, experiment_name):
        """
            Close an experiment
            :param experiment_name:
            :return:
        """
        raise NotImplementedError("MLC::close_experiment not implemented")

    def get_workspace_experiments(self):
        """
            Return a list of the available experiments in the workspace.
            :return: List that contains experiment names.
        """
        raise NotImplementedError("MLC::get_workspace_experiments not implemented")

    def delete_experiment_from_workspace(self, experiment_name):
        """
            Remove an experimento} from the workspace permanently.
            :param experiment_name:
        """
        raise NotImplementedError("MLC::delete_experiment_from_workspace not implemented")

    def new_experiment(self, experiment_name, experiment_configuration):
        """
            Creates a new experiment in the workspace using
            :param experiment_name:
            :param experiment_configuration:
        """
        raise NotImplementedError("MLC::new_experiment not implemented")

    def get_experiment_configuration(self, experiment_name):
        """
            Obtain experiment configuration.
            :param experiment_name:
            :return: experiment configuration.
        """
        raise NotImplementedError("MLC::get_experiment_configuration not implemented")

    def set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value):
        """
            Set a specific parameter value in the experiment configuration.
            :param experiment_name:
            :param section:
            :param parameter:
            :param value:
            :return:
        """
        configuration = {
            param_section: {
                param_name: value
            }
        }
        self.set_experiment_configuration(experiment_name, configuration)

    def set_experiment_configuration(self, experiment_name, configuration):
        """
            Update the experiment configuration
            :param experiment_name:
            :param configuration:
            :return:
        """
        raise NotImplementedError("MLC::set_experiment_configuration not implemented")

    def go(self, experiment_name, to_generation, from_generation=1):
        """
            Execute experiments until to_generation generations are reached.
            :param experiment_name:
            :param to_generation: final generation.
            :param from_generation: initial generation.
            :return:
        """
        raise NotImplementedError("MLC::go not implemented")

    def get_experiment_info(self, experiment_name):
        """
            Obtain experiment information such as, description, amount of
            generations, amount of individuals, etc.
            :param experiment_name:
            :return:
        """
        raise NotImplementedError("MLC::get_experiment_info not implemented")

    def get_generation(self, experiment_name, generation_number):
        """
            Obtain individuals from a specific generation.
            :param experiment_name:
            :param generation_number:
            :return: Generation
        """
        raise NotImplementedError("MLC::get_generation not implemented")

    def get_individuals(self, experiment_name):
        """
            Obtained generated individuals during the simulation.
            :param experiment_name:
            :return:
        """
        raise NotImplementedError("MLC::get_individuals not implemented")


class InvalidExperimentException(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)
