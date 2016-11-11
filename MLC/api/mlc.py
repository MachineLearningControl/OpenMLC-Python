import os
import argparse

from MLC.config import set_working_directory
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation
from MLC.db.mlc_repository import MLCRepository

class ClosedExperimentException(Exception):
    def __init__(self, experiment_name, operation_name):
        Exception.__init__(self, "Cannot execute operation %s because '%s' is closed." % (experiment_name, operation_name))


class ExperimentNotExistException(Exception):
    def __init__(self, experiment_name):
        Exception.__init__(self, "Experiment '%s' does not exist." % experiment_name)


class DuplicatedExperimentError(Exception):
    def __init__(self, experiment_name):
        Exception.__init__(self, "Experiment '%s' already exists." % experiment_name)


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


class MLCLocal(MLC):
    def __init__(self, working_dir):
        if not os.path.exists(working_dir):
            raise Exception("Invalid working directory %s" % working_dir)

        self._working_dir = working_dir

        # Set working dir for the MLC
        set_working_directory(os.path.abspath(self._working_dir))

        self._experiments = {}
        self._open_experiments = {}

        self.log("Searching for experiments in %s" % self._working_dir)

        for _, _, files in os.walk(self._working_dir):
            for file in files:
                if file.endswith('.mlc'):
                    experiment_name = file.split(".")[0]

                    try:
                        configuration, db_file = MLCLocal.check_configuration(self._working_dir, experiment_name)
                        self._experiments[experiment_name] = (configuration, db_file)
                        self.log("Found experiment in workspace: %s" % experiment_name)

                    except InvalidExperimentException, err:
                        self.log("Something go wrong loading experiment '%s': %s" % (experiment_name, err))

        print "Experiments in the workspace: %s" % len(self._experiments)

    def get_workspace_experiments(self):
        return self._experiments.keys()

    def get_experiment_configuration(self, experiment_name):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_configuration", experiment_name)

        return self._open_experiments[experiment_name][0]

    def open_experiment(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        self._open_experiments[experiment_name] = self._experiments[experiment_name]

    def close_experiment(self, experiment_name):
        del self._open_experiments[experiment_name]

    def new_experiment(self, experiment_name, experiment_configuration):
        if experiment_name in self._experiments:
            raise DuplicatedExperimentError(experiment_name)

        # obtain experiment filenames
        experiment_cf, experiment_db = MLCLocal.get_experiment_files(self._working_dir, experiment_name)

        # put DB parameters in the configuration file
        if "BEHAVIOUR" not in experiment_configuration:
            experiment_configuration["BEHAVIOUR"] = {}

        experiment_configuration["BEHAVIOUR"]["save"] = "true"
        experiment_configuration["BEHAVIOUR"]["savedir"] = experiment_name+'.mlc'
        new_configuration = Config.from_dictionary(experiment_configuration)

        # save experiment configuration file
        new_configuration.write(open(experiment_cf, "wt"))

        # create an empty simulation in order to create the experiment database
        MLCRepository._instance = None
        Config._instance = None
        Config.get_instance().read(experiment_cf)
        simulation = Simulation()

        # load experiment
        try:
            configuration, db_file = MLCLocal.check_configuration(self._working_dir, experiment_name)
            self._experiments[experiment_name] = (configuration, db_file)
        except Exception, err:
            self.log("Cannot create a new experiment :( %s " % err)
            raise

    def delete_experiment_from_workspace(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        del self._experiments[experiment_name]
        if experiment_name in self._open_experiments:
            del self._open_experiments[experiment_name]

        experiment_cf, experiment_db = MLCLocal.get_experiment_files(self._working_dir, experiment_name)
        os.unlink(experiment_cf)
        os.unlink(experiment_db)

    def set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration_parameter", experiment_name)

        return MLC.set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value)

    def set_experiment_configuration(self, experiment_name, configuration):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration", experiment_name)

        self._open_experiments[experiment_name][0].update(configuration)
        new_configuration = Config.from_dictionary(self._open_experiments[experiment_name][0])

        # save experiment configuration file
        experiment_cf, experiment_db = MLCLocal.get_experiment_files(self._working_dir, experiment_name)
        new_configuration.write(open(experiment_cf, "wt"))

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
                raise InvalidExperimentException("Invalid DB name configured in %s: is '%s' and should be '%s'" % (experiment_cf, conf_db, experiment_db_name))

            return Config.to_dictionary(config), experiment_db

        except Exception, err:
            raise InvalidExperimentException("Error reading configuration file %s: %s" % (experiment_cf,err))

    def log(self, message):
        print message


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC API Test')

    parser.add_argument('-d', '--working-dir', default='.',
                        type=str, help='MLC working directory.')

    return parser.parse_args()

if __name__ == '__main__':
    arguments = parse_arguments()
    mlc = MLCLocal(working_dir=os.path.abspath(arguments.working_dir))
    experiment = mlc.get_workspace_experiments()
