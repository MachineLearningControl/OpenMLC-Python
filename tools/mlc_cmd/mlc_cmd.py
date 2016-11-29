import os, sys, re, cmd, argparse
import traceback

from MLC.api.mlc import MLCException
from MLC.api.mlc import DuplicatedExperimentError
from MLC.api.mlc import ExperimentNotExistException
from MLC.api.mlc import ClosedExperimentException

from MLC.api.mlc_client import MLCClient
from MLC.api.mlc import MLCLocal

from mlc_cmd_helpers import *


mlc_api = None

this_dir = os.path.dirname(os.path.abspath(__file__))
configuration_file_template = "cmd_default_configuration.ini"

DEFAULT_CONFIGURATION = load_configuration(os.path.join(this_dir,
                                                        configuration_file_template))


def err_handler(exception):
    print ">> Unknown error: %s" % exception

    if MLCCmd.debug_mode:
        traceback.print_exc()


class MLCCmd(cmd.Cmd):
    debug_mode = False
    intro = ""
    current_experiment = None
    prompt = 'mlc>workspace>'

    @validate_params([], err_handler)
    def do_experiments(self):
        self.msg(mlc_api.get_workspace_experiments())

    @validate_params([string, optional(str)], err_handler, "experiment_name [configuration_file] expected.")
    def do_new(self, experiment_name, config_file):

        if config_file is not None:
            self.msg("loading configuration file for experiment '%s' from '%s'." % (experiment_name, config_file))
            experiment_configuration = load_configuration(config_file)
        else:
            self.msg("loading default configuration for experiment '%s'." % experiment_name)
            experiment_configuration = DEFAULT_CONFIGURATION
        try:
            mlc_api.new_experiment(experiment_name, experiment_configuration)
            self.msg("experiment '%s' created." % experiment_name)

        except MLCException, err:
            self.msg(str(err))

    @validate_params([string], err_handler, "experiment_name expected")
    def do_delete(self, experiment_name):

        try:
            mlc_api.delete_experiment_from_workspace(experiment_name)
            self.__on_experiment_close(experiment_name)

            self.msg("experiment '%s' deleted" % experiment_name)

        except MLCException, err:
            self.msg(str(err))

    @validate_params([string], err_handler, "experiment_name expected")
    def do_open(self, experiment_name):
        if MLCCmd.current_experiment is not None:
            self.msg("please close current experiment '%s' before trying to open another one." % (MLCCmd.current_experiment))
            return

        try:
            mlc_api.open_experiment(experiment_name)
            self.__on_experiment_open(experiment_name)

        except MLCException, err:
            self.msg(str(err))

    @validate_params([optional(string)], err_handler, "[experiment_name expected]")
    def do_close(self, experiment_name):

        if experiment_name is None:
            experiment_to_close = MLCCmd.current_experiment
        else:
            experiment_to_close = experiment_name

        if experiment_to_close is None:
            return

        try:
            mlc_api.close_experiment(experiment_to_close)
            self.__on_experiment_close(experiment_to_close)

            self.msg("experiment '%s' closed" % experiment_to_close)

        except MLCException, err:
            self.msg(str(err))

    @validate_params([], err_handler)
    def do_info(self):

        if MLCCmd.current_experiment is None:
            self.msg("no open experiment.")
            return

        experiment_name = MLCCmd.current_experiment

        try:
            experiment_info = mlc_api.get_experiment_info(experiment_name)
            self.msg("Experiment '%s':" % experiment_name)
            for k, v in experiment_info.iteritems():
                self.msg("%s: %s" % (k , v))

        except MLCException, err:
            self.msg(str(err))

    @validate_params([int, optional(int)], err_handler, "to_generation [from_generation] expected")
    def do_go(self, to_generation, from_generation):
        if MLCCmd.current_experiment is None:
            self.msg("no open experiment.")
            return

        try:
            if from_generation is None:
                mlc_api.go(MLCCmd.current_experiment, to_generation)
            else:
                mlc_api.go(MLCCmd.current_experiment, to_generation)

        except MLCException, err:
            self.msg(str(err))

    @validate_params([optional(string), optional(string)], err_handler,"[section] [paramater_name] expected")
    def do_configuration(self, section, parameter_name):
        if MLCCmd.current_experiment is None:
            self.msg("no open experiment.")
            return

        try:
            conf = mlc_api.get_experiment_configuration(MLCCmd.current_experiment)

            if section:
                if section in conf:
                    conf = {section: conf[section]}
                else:
                    self.msg("invalid section name, available sections: %s" % conf.keys())
                    return

            if parameter_name:
                if section:
                    if parameter_name in conf[section]:
                        conf = {section: {parameter_name: conf[section][parameter_name]}}
                    else:
                        self.msg("invalid parameter name, available parameters in section '%s': %s" % (section, conf[section].keys()))
                        return
                else:
                    conf = MLCCmd.__search_parameter_in_configuration(conf, parameter_name)
                    if len(conf.keys()) == 0:
                        self.msg("invalid parameter name")
                        return

            self.__print_configuration(conf)

        except MLCException, err:
            self.msg(str(err))

    @validate_params([string, string, string], err_handler, "section_name paramater_name parameter_value expected")
    def do_set_configuration(self, section, parameter_name, new_value):
        if MLCCmd.current_experiment is None:
            self.msg("no open experiment.")
            return

        conf = mlc_api.get_experiment_configuration(MLCCmd.current_experiment)

        if section not in conf:
            self.msg("invalid section name, available sections: %s" % conf.keys())
            return

        if parameter_name not in conf[section]:
            self.msg("invalid parameter name, available parameters in section '%s': %s" % (section, conf[section].keys()))
            return

        old_value = conf[section][parameter_name]
        mlc_api.set_experiment_configuration_parameter(MLCCmd.current_experiment,
                                                       section, parameter_name,
                                                       new_value)

        self.msg("Parameter '%s' in section '%s' has been modified, old value '%s', new value '%s'" % (parameter_name,
                                                                                                       section,
                                                                                                       new_value,
                                                                                                       old_value))

    def do_quit(self, line):
        return self.__exit()

    def do_exit(self, line):
        return self.__exit()

    def __exit(self):
        return True

    def __print_configuration(self, conf):
        for section, parameters in conf.iteritems():
            print "[%s]" % (section,)
            for name, value in parameters.iteritems():
                print "    %s = %s" % (name, value)

    @staticmethod
    def __search_parameter_in_configuration(configuration, param_name):
        found = {}
        for section, parameters in configuration:
            for name, value in parameters.iteritems():
                if name == param_name:
                    found[section] = {name: value}

        return found

    def msg(self, message):
        print ">> " + str(message)

    def __on_experiment_open(self, experiment_name):
        MLCCmd.current_experiment = experiment_name
        MLCCmd.prompt = 'mlc>workspace>' + experiment_name + ">"

    def __on_experiment_close(self, experiment_name):
        if MLCCmd.current_experiment == experiment_name:
            MLCCmd.prompt = 'mlc>workspace>'

        MLCCmd.current_experiment = None


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC Cmd Tool (Local and Remote Version)')

    parser.add_argument('--remote', action='store_true',
                        help='If remote is enabled MLC Cmd will try to connect to the MLC Server at http://[mlc-server-hostname]:[mlc-server-port] '
                             'else MLC will loads a local workspace from [workspace-directory]')

    parser.add_argument('-s', '--mlc-server-hostname', default="127.0.0.1",
                        type=str, help='MLC server hostname.')

    parser.add_argument('-p', '--mlc-server-port', default=5000,
                        type=int, help='MLC Server listening port.')

    parser.add_argument('-w', '--workspace-dir',
                        type=str, help='MLC Server local workspace directory.')

    parser.add_argument('--debug-mode', action='store_true',
                        help='Enable debug mode for the MLC Cmd Tool.')

    arguments = parser.parse_args()

    if not arguments.remote and arguments.workspace_dir is None:
        parser.print_help()
        print "missing working-dir for Local Cmd Tool."
        sys.exit(1)

    return arguments

if __name__ == '__main__':

    arguments = parse_arguments()

    if arguments.debug_mode:
        print ">> Executing MLC Cmd Tool in debug mode"
        MLCCmd.debug_mode = True

    if arguments.remote:
        MLCCmd.intro = "Remote MLC Cmd Tool, connected to MLC at http://%s:%s" % (arguments.mlc_server_hostname,
                                                                                  arguments.mlc_server_port)

        mlc_api = MLCClient(arguments.mlc_server_hostname,  arguments.mlc_server_port)
    else:
        MLCCmd.intro = "Local MLC Cmd Tool, loading workspace from %s" % arguments.workspace_dir

        mlc_api = MLCLocal(arguments.workspace_dir)

    MLCCmd().cmdloop()