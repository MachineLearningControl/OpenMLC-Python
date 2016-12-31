import argparse
import ConfigParser
import os

from MLC.api.Experiment import Experiment
from MLC.api.mlc import MLC
from MLC.api.mlc import ClosedExperimentException
from MLC.api.mlc import ExperimentNotExistException
from MLC.api.mlc import DuplicatedExperimentError
from MLC.Application import Application
from MLC.config import set_working_directory
from MLC.db.mlc_repository import MLCRepository
from MLC.Log.log import get_gui_logger
from MLC.mlc_parameters.config_rules import MLCConfigRules
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation

logger = get_gui_logger()


class MLCLocal(MLC):

    def __init__(self, working_dir):
        if not os.path.exists(working_dir):
            raise Exception("Invalid working directory %s" % working_dir)

        self._working_dir = working_dir

        # Set working dir for the MLC
        set_working_directory(os.path.abspath(self._working_dir))

        self._experiments = {}
        self._open_experiments = {}

        logger.info("[MLC_LOCAL] [INIT] - Searching for experiments in {0}".format(self._working_dir))
        workspace_files = os.listdir(working_dir)
        project_names = set([x.split(".")[0] for x in workspace_files])

        # Now, check if every possible project name has a .mlc and .cfg file associated
        for name in project_names:
            mlc_file = name + ".mlc"
            cfg_file = name + ".conf"

            if mlc_file in workspace_files and cfg_file in workspace_files:
                try:
                    self._experiments[name] = Experiment(self._working_dir, name)
                    logger.debug('[MLC_LOCAL] [INIT] - Found experiment in workspace: {0}'.format(name))
                except InvalidExperimentException, err:
                    logger.debug("[MLC_LOCAL] [INIT] - Something go wrong loading experiment '{0}': {1}" % (name, err))
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
        experiment_configuration["BEHAVIOUR"]["savedir"] = experiment_name + '.mlc'
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
        experiment_files = [experiment_cf, experiment_db]

        for file in experiment_files:
            try:
                os.unlink(file)
            except OSError:
                logger.info("[MLC_LOCAL] Error while tryying to delete experiment file: {0}".format(file))

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
            "individuals": MLCRepository.get_instance().number_of_individuals(),
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
        for indiv_id in range(1, number_of_individuals + 1):
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


def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC API Test')

    parser.add_argument('-d', '--working-dir', default='.',
                        type=str, help='MLC working directory.')

    return parser.parse_args()
