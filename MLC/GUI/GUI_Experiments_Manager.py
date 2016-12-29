import os
import sys
import time
sys.path.append(os.path.abspath(".") + "/../..")

from MLC.Log.log import get_gui_logger

logger = get_gui_logger()

"""
Object that will encapsulate all the operations related with the ABM of projects
"""

class GUI_Experiments_Manager():

    def __init__(self, mlc_local, gui_config):
        self._gui_config = gui_config
        self._mlc_local = mlc_local

        self._experiment_list = []
        self._experiment_info_dict = {}

    def load_experiments_info(self):
        # Clean the experiment list before filling it
        start_time = time.time()
        self._experiment_list = []

        # Find all the projects in the workspace directory
        workspace_dir = self._gui_config.get('MAIN', 'workspace')
        workspace_files = os.listdir(workspace_dir)

        # Get a list of the possible projects names
        project_names = set([x.split(".")[0] for x in workspace_files])
        logger.debug('[GUI_EXPERIMENT_MANAGER] [LOAD_EXPERIMENTS_INFO] - Files in workspace directory: {0}'.format(workspace_files))
        logger.debug('[GUI_EXPERIMENT_MANAGER] Possible project names: {0}'.format(project_names))

        # Now, check if every possible project name has a .mlc and .cfg file associated
        for name in project_names:
            mlc_file = name + ".mlc"
            cfg_file = name + ".conf"
            if mlc_file in workspace_files and cfg_file in workspace_files:
                logger.debug('[GUI_EXPERIMENT_MANAGER] [LOAD_EXPERIMENTS_INFO] - Valid project: {0}'.format(name))
                self._experiment_list.append(name)

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
        pass

    def remove_experiment(self, experiment_name):
        pass

    def get_experiment_list(self):
        return self._experiment_list

    def get_experiment_info(self, experiment_name):
        try:
            return self._experiment_info_dict[experiment_name]
        except KeyError:
            logger.debug("[GUI_EXPERIMENT_MANAGER] [GET_EXPERIMENTS_INFO] - Experiment {0} info not found.")

        return None
