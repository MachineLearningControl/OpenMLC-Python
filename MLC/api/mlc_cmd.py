import cmd
import re
import argparse
import ConfigParser
from MLC.mlc_parameters.mlc_parameters import Config

from mlc_client import MLCClient
from mlc import MLCLocal

mlc_api = None


def validate_params(param_types, fail_message=""):
    def decorator(func):
        def real_decorator(*args, **kwargs):
            self, line = args
            input_values = line.split()

            if len(input_values) > len(param_types):
                print "Bad command arguments, %s" % fail_message
                return False

            input_values = input_values + [None]*(len(param_types) - len(input_values))
            validated_values = None

            try:
                type_values = zip(param_types, input_values)
                print type_values
                validated_values = [t(v) for t, v in type_values]
            except Exception, err:
                print "Bad command arguments, %s" % fail_message
                return False

            return func(self, *validated_values)

        return real_decorator
    return decorator


def string(value):
    if value is None:
        raise ValueError("null_value, expected string_value")
    return str(value)


def optional(value_type):
    def validate(value):
        if value is not None:
            return value_type(value)
    return validate


class MLCCmd(cmd.Cmd):
    intro = ""
    open_experiment = None
    prompt = 'mlc>workspace>'

    @validate_params([])
    def do_experiments(self):
        print mlc_api.get_workspace_experiments()

    @validate_params([string, optional(str)], "experiment_name, [configuration_file] expected")
    def do_new(self, experiment_name, config_file):

        experiment_configuration = None

        if config_file is None:
            experiment_configuration = {"POPULATION":
                                            {"size": "100",
                                             "sensors": "1",
                                             "sensor_spec": "false",
                                             "sensor_list": "1, 5, 2, 4"}
                                        }
        else:
            config = ConfigParser.ConfigParser()
            config.read(splitted_line[1])
            experiment_configuration = Config.to_dictionary(config)

        print experiment_name
        print config_file
        return

        if len(splitted_line) == 1:
            experiment_name = line

        else:
            experiment_name = splitted_line[0]


        try:
            mlc_api.new_experiment(experiment_name, experiment_configuration)

        except Exception, err:
            self.__msg("Cannot create the experiment, cause: %s" % err)

    def do_delete(self, line):
        if not re.match(r"[^\s]+", line):
            self.__msg("Argument error, an experiment name was expected")

        experiment_name = line

        try:
            mlc_api.delete_experiment_from_workspace(experiment_name)
            self.__close_experiment(experiment_name)

        except Exception, err:
            self.__msg("Error deleting experiment, cause: %s" % err)

    def do_close(self, line):
        pass

    def do_quit(self, line):
        return self.__exit()

    def do_exit(self, line):
        return self.__exit()

    def __exit(self):
        return True

    def msg(self, message):
        print message

    def __open_experiment(self, experiment_name):
        MLCCmd.open_experiment = experiment_name
        MLCCmd.prompt = 'mlc>workspace>' + experiment_name + ">"

    def __close_experiment(self, experiment_name):
        MLCCmd.open_experiment = None
        MLCCmd.prompt = 'mlc>workspace>'


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
        raise Exception("Missing working-dir for Local Cmd Tool.")

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