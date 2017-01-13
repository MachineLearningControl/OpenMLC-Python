import ConfigParser
import os
import sys
import time
sys.path.append(os.path.abspath(".") + "/../..")

from MLC.api.mlc import DuplicatedExperimentError
from MLC.Log.log import get_gui_logger
from MLC.mlc_parameters.mlc_parameters import Config

logger = get_gui_logger()

"""
Object that will encapsulate all the operations related with the ABM of projects
"""

class ExperimentsManager():
    DEFAULT_EXPERIMENT_CONFIG = "../../conf/configuration.ini"

    def __init__(self, mlc_local, gui_config):
        self._gui_config = gui_config
        self._mlc_local = mlc_local

        self._experiment_list = []
        self._experiment_info_dict = {}

        # Config file used to create new projects
        default_experiment_config = ConfigParser.ConfigParser()
        default_experiment_config.read(ExperimentsManager.DEFAULT_EXPERIMENT_CONFIG)
        self._default_experiment_config = Config.to_dictionary(default_experiment_config)

    def load_experiments_info(self):
        # Clean the experiment list before filling it
        start_time = time.time()
        self._experiment_list = []

        # Find all the projects in the workspace directory
        workspace_dir = self._gui_config.get('MAIN', 'workspace')
        self._experiment_list = self._mlc_local.get_workspace_experiments()

        logger.info('[GUI_EXPERIMENT_MANAGER] [LOAD_EXPERIMENTS_INFO] - Projects in the workspace: {0}'.format(self._experiment_list))
        self._experiment_list.sort()
        self._load_experiment_info_per_project()

        elapsed_time = time.time() - start_time
        logger.debug("[GUI_EXPERIMENT_MANAGER] [LOAD_EXPERIMENTS_INFO] - Experiments info updated. Time elapsed: {0}".format(elapsed_time))

    def _load_experiment_info_per_project(self):
        self._experiment_info_dict = {}
        for experiment_name in self._experiment_list:
            self.load_experiment_info(experiment_name)

    def load_experiment_info(self, experiment_name):
        start_time = time.time()
        self._mlc_local.open_experiment(experiment_name)
        experiment_info = self._mlc_local.get_experiment_info(experiment_name)
        self._mlc_local.close_experiment(experiment_name)

        # Update the experiment description
        description = ""
        for key, value in experiment_info.iteritems():
            description += "<b>" + str(key) + ":</b> " + str(value) + "<br>"
        self._experiment_info_dict[experiment_name] = description

        # Log the amount of time spent in every experiment info update
        amount_individuals = experiment_info["individuals"]
        elapsed_time = time.time() - start_time
        logger.debug("[GUI_EXPERIMENT_MANAGER] [LOAD_EXPERIMENTS_INFO] - Experiment {0} info updated. "
                     "Amount Individuals: {1}. Time elapsed: {2}"
                     .format(experiment_name, amount_individuals, elapsed_time))

    def add_experiment(self, experiment_name):
        try:
            self._mlc_local.new_experiment(experiment_name, self._default_experiment_config)
            logger.info("[GUI_EXPERIMENT_MANAGER] [ADD_EXPERIMENT] - "
                        "Added experiment {0}".format(experiment_name))
        except DuplicatedExperimentError:
            logger.debug("[GUI_EXPERIMENT_MANAGER] [ADD_EXPERIMENT] - "
            "Added experiment {0}".format(experiment_name))
            return False

        # Experiment succesfully loaded. Update its experiment_info
        self._experiment_list.append(experiment_name)
        self.load_experiment_info(experiment_name)
        return True

    def add_experiment_even_if_repeated(self, experiment_name):
        if experiment_name in self._experiment_list:
            logger.debug("[GUI_EXPERIMENT_MANAGER] [ADD_EXPERIMENT_EVEN_IF_REPEATED] "
                         "Proceed to remove a experiment without one of its files")
            self._mlc_local.delete_experiment_from_workspace(experiment_name)

        self.add_experiment(experiment_name)

    def remove_experiment(self, experiment_name):
        workspace_dir = self._gui_config.get('MAIN', 'workspace')
        experiment_full_path = workspace_dir + '/'
        experiment_files = [experiment_name + ".mlc", experiment_name + ".conf"]

        # Check if the files to remove exists
        if set(experiment_files) <= set(os.listdir(workspace_dir)):
            # Try to remove the files
            try:
                self._mlc_local.delete_experiment_from_workspace(experiment_name)
            except OSError:
                logger.error("[GUI_EXPERIMENT_MANAGER] [REMOVE_EXPERIMENT] - "
                             "Experiment file {0} could not be removed".format(file))
                return True, False
        else:
            logger.error("[GUI_EXPERIMENT_MANAGER] [REMOVE_EXPERIMENT] - "
                         "Experiment {0} can't be removed. Some of the project files is missing"
                         .format(experiment_name))
            return False, True

        self._experiment_list.remove(experiment_name)
        del self._experiment_info_dict[experiment_name]
        return False, False

    def get_experiment_list(self):
        return self._experiment_list

    def get_experiment_info(self, experiment_name):
        try:
            return self._experiment_info_dict[experiment_name]
        except KeyError:
            logger.debug("[GUI_EXPERIMENT_MANAGER] [GET_EXPERIMENTS_INFO] - Experiment {0} info not found.")

        return None
