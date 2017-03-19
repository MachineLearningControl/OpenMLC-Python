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


class EvaluationScriptNotExistException(MLCException):

    def __init__(self, experiment_name, script_path):
        MLCException.__init__(self, "Experiment {0} is trying to use a non "
                                    "existent evaluation script. Script: {1}"
                                    .format(experiment_name, script_path))


class PreevaluationScriptNotExistException(MLCException):

    def __init__(self, experiment_name, script_path):
        MLCException.__init__(self, "Experiment {0} is trying to use a non "
                                    "existent evaluation script. Script: {1}"
                                    .format(experiment_name, script_path))


class ImportExperimentPathNotExistException(MLCException):

    def __init__(self, experiment_path):
        MLCException.__init__(self, "Import Experiment Error: Path {0} does not exists."
                                    .format(experiment_path))


class ConfigFilePathNotExistException(MLCException):

    def __init__(self, config_file_path):
        MLCException.__init__(self, "Config File Error: Path {0} does not exists."
                                    .format(experiment_path))


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

    def new_experiment(self, experiment_name, experiment_configuration):
        """
            Creates a new experiment in the workspace using
            :param experiment_name:
            :param experiment_configuration: The experiment configuration as a
             Python dict of dict
        """
        raise NotImplementedError("MLC::new_experiment not implemented")

    def delete_experiment(self, experiment_name):
        """
            Remove an experiment from the workspace permanently.
            :param experiment_name:
        """
        raise NotImplementedError("MLC::delete_experiment not implemented")

    def clone_experiment(self, experiment_name, cloned_experiment):
        """
            Clone an experiment from the workspace.
            :param experiment_name:
            :param cloned_experiment
        """
        raise NotImplementedError("MLC::cloned_experiment not implemented")

    def import_experiment(self, experiment_path):
        """
            Import an experiment and add it to the workspace
            :param experiment_path:
        """
        raise NotImplementedError("MLC::import_experiment not implemented")

    def export_experiment(self, experiment_name):
        """
            Import an experiment and add it to the workspace
            :param export_dir: Directory where the project will be exported
            :param experiment_name: Name of the experiment to be exported
            :return: The project as a file in a variable
        """
        raise NotImplementedError("MLC::export_experiment not implemented")

    def get_experiment_configuration(self, experiment_name):
        """
            Obtain experiment configuration.
            :param experiment_name:
            :return: experiment configuration.
        """
        raise NotImplementedError("MLC::get_experiment_configuration not implemented")

    def reload_experiment_configuration(self, experiment_name):
        """
            Load again the experiment configuration.
            :param experiment_name:
            :return: experiment configuration.
        """
        raise NotImplementedError("MLC::reload_experiment_configuration not implemented")

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

    def set_experiment_configuration_from_file(self, experiment_name, experiment_filepath):
        """
            Update the experiment configuration from a config file
            :param experiment_name:
            :param configuration: Configuration file, as a filesystem path
            :return:
        """
        raise NotImplementedError("MLC::set_experiment_configuration_from_file not implemented")

    def set_experiment_configuration(self, experiment_name, configuration):
        """
            Update the experiment configuration
            :param experiment_name:
            :param configuration:
            :return:
        """
        raise NotImplementedError("MLC::set_experiment_configuration not implemented")

    def go(self, experiment_name, to_generation,
           from_generation=0, callbacks={}, gen_creator=None):
        """
            Execute experiments until to_generation generations are reached.
            :param experiment_name:
            :param to_generation: final generation.
            :param from_generation: initial generation.
            :param callbacks: Callbacks to be triggered in special moments of the experiment
            :param gen_creator: Modified gen_creator to add individuals manually
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

    def remove_generations_from(self, experiment_name, gen_number):
        """
        Remove all the generations above the given as a parameter (include the gen given)
        :param experiment_name
        :param gen_number
        """

    def remove_generations_to(self, experiment_name, gen_number):
        """
        Remove all the generations below the given as a parameter (include the gen given)
        the one passed as an argument
        :param experiment_name
        :param gen_number
        """

    def get_individuals(self, experiment_name):
        """
            Obtained generated individuals during the simulation.
            :param experiment_name:
            :return:
        """
        raise NotImplementedError("MLC::get_individuals not implemented")

    def get_individual(self, experiment_name, individual_id):
        """
            Obtained generated individuals during the simulation.
            :param experiment_name:
            :return:
        """
        raise NotImplementedError("MLC::get_individual not implemented")

    def update_individual_cost(self, experiment_name, indiv_id,
                               new_cost, new_ev_time, generation=-1):
        """
            Update individual cost. If generation == -1 Individual cost will
            be updated in all generations.
            :param experiment_name:
            :return:
        """
        raise NotImplementedError("MLC::get_individuals not implemented")

    def show_best(self, experiment_name, generation_number):
        """
        Plot the best individual of the populations evaluated. This method ought not
        to be called before calling the function go at least once
        :param experiment_name:
        :param generation_number: The generation in which we are looking
        for the best individual
        """
        raise NotImplementedError("MLC::get_individuals not implemented")


class InvalidExperimentException(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)
