import os
import argparse
import ConfigParser

from MLC.config import set_working_directory
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation
from MLC.db.mlc_repository import MLCRepository
from MLC.Application import Application
from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.config_rules import MLCConfigRules

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
        MLCConfigRules
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
            self._simulation = Simulation()
            Experiment.__last_simulation = self._simulation

        return self._simulation

    def get_configuration(self):
        return Config.to_dictionary(self._configuration)

    def set_configuration(self, new_configuration):
        self._configuration = Config.from_dictionary(new_configuration, config_type=ConfigParser.ConfigParser)
        self._configuration.write(open(self._config_file, "wt"))

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


class MLCLocal(MLC):

    def __init__(self, working_dir):
        if not os.path.exists(working_dir):
            raise Exception("Invalid working directory %s" % working_dir)

        self._working_dir = working_dir

        # Set working dir for the MLC
        set_working_directory(os.path.abspath(self._working_dir))

        self._experiments = {}
        self._open_experiments = {}

        # self.log("Searching for experiments in %s" % self._working_dir)

        for item in os.listdir(self._working_dir):
            if os.path.isfile(os.path.join(self._working_dir, item)):
                file = item
                if file.endswith('.mlc'):
                    experiment_name = file.split(".")[0]

                    try:
                        self._experiments[experiment_name] = Experiment(self._working_dir, experiment_name)
                        # self.log("Found experiment in workspace: %s" % experiment_name)

                    except InvalidExperimentException, err:
                        # self.log("Something go wrong loading experiment '%s': %s" % (experiment_name, err))
                        pass
        # print "Experiments in the workspace: %s" % len(self._experiments)

    def get_workspace_experiments(self):
        return self._experiments.keys()

    def get_experiment_configuration(self, experiment_name):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_configuration", experiment_name)

        return self._open_experiments[experiment_name].get_configuration()

    def open_experiment(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        self._open_experiments[experiment_name] = self._experiments[experiment_name]

    def close_experiment(self, experiment_name):
        del self._open_experiments[experiment_name]

    # TODO: moves this method to Experiment class
    def new_experiment(self, experiment_name, experiment_configuration):
        if experiment_name in self._experiments:
            raise DuplicatedExperimentError(experiment_name)

        # obtain experiment filenames
        experiment_cf, experiment_db = Experiment.get_experiment_files(self._working_dir, experiment_name)

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
            configuration, db_file = Experiment.check_configuration(self._working_dir, experiment_name)
            self._experiments[experiment_name] = Experiment(self._working_dir, experiment_name)
        except Exception, err:
            # self.log("Cannot create a new experiment :( %s " % err)
            raise

    def delete_experiment_from_workspace(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        del self._experiments[experiment_name]
        if experiment_name in self._open_experiments:
            del self._open_experiments[experiment_name]

        experiment_cf, experiment_db = Experiment.get_experiment_files(self._working_dir, experiment_name)
        os.unlink(experiment_cf)
        os.unlink(experiment_db)

    def set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration_parameter", experiment_name)

        return MLC.set_experiment_configuration_parameter(self, experiment_name, param_section, param_name, value)

    def set_experiment_configuration(self, experiment_name, new_configuration):
        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("set_experiment_configuration", experiment_name)

        for section, params in new_configuration.iteritems():
            for param_name, param_value in new_configuration[section].iteritems():
                MLCConfigRules.get_instance().apply(section, param_name, param_value, self._open_experiments[experiment_name].get_simulation())

        experiment = self._open_experiments[experiment_name]
        configuration = experiment.get_configuration()

        for section, params in new_configuration.iteritems():
            for param_name, param_value in new_configuration[section].iteritems():
                configuration[section][param_name] = new_configuration[section][param_name]

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
            "individuals": MLCRepository.get_instance().number_of_individuals(),
            "individuals_per_generation": Config.get_instance().getint("POPULATION", "size"),
            "filename": experiment_name+".mlc"
        }

        return experiment_info

    def go(self, experiment_name, to_generation, from_generation=0):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # load simulation
        experiment = self._open_experiments[experiment_name]
        simulation = experiment.get_simulation()

        # launch simulation
        app = Application(simulation)
        app.go(from_generation=from_generation, fig=0, to_generation=to_generation)

        return True

    # TODO: Individuals must be represented using dictionaries in the MLC API
    def get_individuals(self, experiment_name):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # get simulation in order to load mlc experiment database
        simulation = self._open_experiments[experiment_name].get_simulation()

        # obtain individuals from the database
        individuals = []
        number_of_individuals = MLCRepository.get_instance().number_of_individuals()
        for indiv_id in range(1, number_of_individuals+1):
            individual = MLCRepository.get_instance().get_individual(indiv_id)
            individuals.append(individual)

        return individuals

    # TODO: Population must be represented using dictionaries/lists in the MLC API
    def get_generation(self, experiment_name, generation_number):
        if experiment_name not in self._experiments:
            raise ExperimentNotExistException(experiment_name)

        if experiment_name not in self._open_experiments:
            raise ClosedExperimentException("get_experiment_info", experiment_name)

        # get simulation in order to load mlc experiment database
        simulation = self._open_experiments[experiment_name].get_simulation()

        return simulation.get_generation(generation_number)

    def log(self, message):
        print message


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC API Test')

    parser.add_argument('-d', '--working-dir', default='.',
                        type=str, help='MLC working directory.')

    return parser.parse_args()
