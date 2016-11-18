import os, sys, re, cmd, argparse
import ConfigParser

from MLC.mlc_parameters.mlc_parameters import Config
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


class MLCCmd(cmd.Cmd):
    intro = ""
    current_experiment = None
    prompt = 'mlc>workspace>'

    @validate_params([])
    def do_experiments(self):
        try:
            self.msg(mlc_api.get_workspace_experiments())

        except Exception, err:
            self.msg("cannot obtain experiment from the workspace, cause %s." % err)

    @validate_params([string, optional(str)], "experiment_name [configuration_file] expected.")
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

        except DuplicatedExperimentError:
            self.msg("an experiment with that name already exists.")

        except Exception, err:
            self.msg("cannot create the experiment, cause: %s." % err)

    @validate_params([string], "experiment_name expected")
    def do_delete(self, experiment_name):

        try:
            mlc_api.delete_experiment_from_workspace(experiment_name)
            self.__on_experiment_close(experiment_name)

            self.msg("experiment '%s' deleted" % experiment_name)

        except ExperimentNotExistException:
            self.msg("experiment '%s' does not exist in the workspace." % experiment_name)

        except Exception, err:
            self.msg("cannot delete experiment, cause: %s" % err)

    @validate_params([string], "experiment_name expected")
    def do_open(self, experiment_name):
        if MLCCmd.current_experiment is not None:
            self.msg("please close current experiment '%s' before trying to open another one." % (MLCCmd.current_experiment))
            return

        try:
            mlc_api.open_experiment(experiment_name)
            self.__on_experiment_open(experiment_name)

        except ExperimentNotExistException:
            self.msg("experiment '%s' does not exist in the workspace." % experiment_name)

        except Exception, err:
            self.msg("cannot open experiment, cause: %s" % err)

    @validate_params([optional(string)], "[experiment_name expected]")
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

        except ExperimentNotExistException:
            self.msg("experiment '%s' does not exist in the workspace." % experiment_to_close)

        except Exception, err:
            self.msg("cannot close experiment, cause: %s" % err)

    @validate_params([])
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

        except ExperimentNotExistException:
            self.msg("experiment '%s' does not exist in the workspace." % experiment_name)

        except ClosedExperimentException:
            self.msg("experiment '%s' is closed" % experiment_name)

        except Exception, err:
            self.msg("cannot obtain experiment info, cause: %s" % type(err))

    @validate_params([int, optional(int)], "to_generation [from_generation] expected")
    def do_go(self, to_generation, from_generation):
        if MLCCmd.current_experiment is None:
            self.msg("no open experiment.")
            return

        try:
            if from_generation is None:
                mlc_api.go(MLCCmd.current_experiment, to_generation)
            else:
                mlc_api.go(MLCCmd.current_experiment, to_generation)

        except ExperimentNotExistException:
            self.msg("experiment '%s' does not exist in the workspace." % MLCCmd.current_experiment)

        except ClosedExperimentException:
            self.msg("experiment '%s' is closed" % MLCCmd.current_experiment)

        except Exception, err:
            self.msg("cannot execute experiment info, cause: %s" % err)

    def do_quit(self, line):
        return self.__exit()

    def do_exit(self, line):
        return self.__exit()

    def __exit(self):
        return True

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

    arguments = parser.parse_args()

    if not arguments.remote and arguments.workspace_dir is None:
        parser.print_help()
        print "missing working-dir for Local Cmd Tool."
        sys.exit(1)

    return arguments

if __name__ == '__main__':

    arguments = parse_arguments()

    if arguments.remote:
        MLCCmd.intro = "Remote MLC Cmd Tool, connected to MLC at http://%s:%s" % (arguments.mlc_server_hostname,
                                                                                  arguments.mlc_server_port)

        mlc_api = MLCClient(arguments.mlc_server_hostname,  arguments.mlc_server_port)
    else:
        MLCCmd.intro = "Local MLC Cmd Tool, loading workspace from %s" % arguments.workspace_dir

        mlc_api = MLCLocal(arguments.workspace_dir)

    MLCCmd().cmdloop()