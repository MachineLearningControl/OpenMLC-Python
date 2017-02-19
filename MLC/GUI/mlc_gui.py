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

import os
import sys
sys.path.append(os.path.abspath(".") + "/../..")

import ConfigParser
import tarfile
import time
import yaml

from MLC.api.MLCLocal import MLCLocal
from MLC.api.MLCLocal import DuplicatedExperimentError
from MLC.GUI.ExperimentsManager import ExperimentsManager
from MLC.GUI.Autogenerated.autogenerated import Ui_MLCManager
from MLC.GUI.Autogenerated.autogenerated import Ui_PropertiesDialog
from MLC.GUI.Experiment.ExperimentWindow import ExperimentWindow
from MLC.GUI.Tables.ConfigParserTableModel import ConfigParserTableModel
from MLC.Log.log import get_gui_logger

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox

logger = get_gui_logger()


class MLC_GUI(QMainWindow):
    MLC_ICON_FILE = "./images/mlc_icon.png"
    GUI_CONFIG_FILE = "./.mlc_gui.conf"
    WEBSERVICE_PORT = 5000
    experiment_closed = pyqtSignal(['QString'])

    def __init__(self):
        QMainWindow.__init__(self)

        # set mlc icon image
        self.setWindowIcon(QIcon(self.MLC_ICON_FILE))

        self._autogenerated_object = Ui_MLCManager()
        self._autogenerated_object.setupUi(self)

        # ConfigParser instance with the config related with the MLC Manager (not an experiment)
        self._gui_config = None
        self._experiments_manager = None
        # Store the name of the element selected in the experiment_list. The experiment selected is the
        # one highlighted in the experiment_list
        self._experiment_selected = None
        # UI Equivalent to MLC_GUI. Class with the responsability of create, remove, and execute experiments
        self._mlc_local = None

        # When an ExperimentDialog is closed, update the experiment info
        self.experiment_closed.connect(self.load_and_refresh_experiment_info)

    def on_new_button_clicked(self):
        logger.debug('[MLC_MANAGER] [NEW_EXPERIMENT] - New experiment button clicked')
        experiment_name = ""
        dialog_ok = False

        while True:
            experiment_name, dialog_ok = QInputDialog.getText(self, 'New Experiment',
                                                              'Enter the name of the new experiment to be created:')

            if dialog_ok:
                if experiment_name == "":
                    logger.info('[MLC_MANAGER] [NEW_EXPERIMENT] - New experiment cannot an empty string.')
                    msg_ok = QMessageBox.information(self, 'New Experiment',
                                                     'New experiment cannot be an empty string. Please, insert a valid name',
                                                     QMessageBox.Ok | QMessageBox.Cancel,
                                                     QMessageBox.Ok)

                    if msg_ok == QMessageBox.Ok:
                        continue
                    else:
                        break

                # Check if the experiment already exists
                if experiment_name in self._experiments_manager.get_experiment_list():
                    msg_ok = QMessageBox.question(self, 'New Experiment',
                                                  ('The experiment name has already been taken. '
                                                   'Do you want to create a project with a different name?'),
                                                  QMessageBox.Yes | QMessageBox.No,
                                                  QMessageBox.Yes)
                    if msg_ok == QMessageBox.Yes:
                        continue
                    else:
                        break

                # Create the new experiment and refresh the View
                self._experiments_manager.add_experiment_even_if_repeated(experiment_name)
                self._refresh_experiment_list_view()
                self._clean_experiment_selection()

                QMessageBox.information(self, 'New Experiment',
                                        'New experiment was succesfully created')
                logger.debug('[MLC_MANAGER] [NEW_EXPERIMENT] - New experiment was succesfully '
                             'created. Name: {0}'.format(experiment_name))
                return
            else:
                break
        logger.debug('[MLC_MANAGER] New experiment could not be created')

    def on_open_button_clicked(self):
        logger.debug("[MLC_MANAGER] [OPEN_BUTTON] - Open button clicked")
        if self._experiment_selected is None:
            logger.info("[MLC MANAGER] [OPEN_BUTTON] - No experiment was selected yet. Don't do anything")
            return

        experiment = ExperimentWindow(mlc_local=self._mlc_local,
                                      experiment_name=self._experiment_selected,
                                      experiment_closed_signal=self.experiment_closed,
                                      parent=self)
        experiment.show()

    def on_clone_button_clicked(self):
        logger.debug("[MLC_MANAGER] [CLONE_BUTTON] - Open button clicked")
        # TODO

    def on_remove_button_clicked(self):
        logger.debug("[MLC_MANAGER] [REMOVE_EXPERIMENT] - Remove button clicked")
        if self._experiment_selected is None:
            logger.info("[MLC MANAGER] [REMOVE_EXPERIMENT] - No experiment was selected yet. Don't do anything")
            return

        msg_ok = QMessageBox.question(self, 'Remove Experiment',
                                      "Do you really want to remove experiment '{0}'?."
                                      .format(self._experiment_selected),
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)
        if msg_ok == QMessageBox.Yes:
            experiment_removed = self._experiments_manager.remove_experiment(self._experiment_selected)
            if not experiment_removed:
                logger.error("[MLC_MANAGER] [REMOVE_EXPERIMENT] - {0} experiment files could not be removed"
                             .format(self._experiment_selected))
                QMessageBox.critical(self, 'Remove Experiment', '{0} experiment file could not be removed.'
                                           'Check if you have the right permissions over the files in the '
                                           'workspace folder'.format(self._experiment_selected))
                return

            QMessageBox.information(self, "Remove Experiment",
                                    "Experiment {0} was succesfully removed".format(self._experiment_selected))
            self._refresh_experiment_list_view()
            self._clean_experiment_selection()
            logger.info("[MLC_MANAGER] [REMOVE_EXPERIMENT] - Experiment {0} was succesfully removed"
                        .format(self._experiment_selected))

    def on_import_button_clicked(self):
        logger.debug("[MLC_MANAGER] [IMPORT_BUTTON] - Import button clicked")
        # Get the path of the experiment to import
        tar_path = QFileDialog.getOpenFileName(self, "Import Experiment", ".",
                                               "MLC Experiment File (*.mlc)")[0]
        if not tar_path:
            # User clicked 'Cancel' or simply closed the Dialog
            return

        experiment_name = os.path.split(tar_path)[1].split(".")[0]
        try:
            self._experiments_manager.import_experiment(tar_path)
            QMessageBox.information(self, "Import Experiment",
                                    "Experiment {0} was succesfully imported"
                                    .format(experiment_name))
            self._refresh_experiment_list_view()
            self._clean_experiment_selection()
        except DuplicatedExperimentError:
            QMessageBox.critical(self, "Import Experiment", "Experiment {0} could not be imported. "
                                 "It already exists.".format(experiment_name))
        except Exception, err:
            QMessageBox.critical(self, "Import Experiment", "Experiment {0} could not be imported. {1}"
                                 .format(experiment_name, err))

    def on_export_button_clicked(self):
        logger.debug("[MLC_MANAGER] [EXPORT_BUTTON] - Export button_clicked")
        if self._experiment_selected is None:
            logger.info("[MLC_MANAGER] [EXPORT_BUTTON] - No experiment was selected yet. Don't do anything")
            return

        export_dir = QFileDialog.getExistingDirectory(self, 'Choose the directory where to export the experiment',
                                                      '.', QFileDialog.ShowDirsOnly)

        if not export_dir:
            # User clicked 'Cancel' or simply closed the Dialog
            return

        try:
            self._experiments_manager.export_experiment(export_dir, self._experiment_selected)
            QMessageBox.information(self, "Experiment Exported",
                                    "Experiment {0} was succesfully exported. It is stored in {1}"
                                    .format(self._experiment_selected, export_dir))
        except Exception, err:
            QMessageBox.critical(self, "Experiment Not Exported",
                                 "Experiment could not be exported. "
                                 "Error {0}".format(err))

    def load_gui_config(self):
        abspath = os.path.abspath(".")
        config_filepath = os.path.join(abspath, MLC_GUI.GUI_CONFIG_FILE)

        if not os.path.isfile(config_filepath):
            reply = QMessageBox.question(self, 'Message',
                                         "Workspace has not been set yet. Do you want to set it?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                workspace_dir = QFileDialog.getExistingDirectory(self, 'Set workspace Directory',
                                                                 '.', QFileDialog.ShowDirsOnly)
                if workspace_dir == "":
                    QMessageBox.critical(self, 'MLC Manager',
                                         'Workspace has not been set. Aborting program',
                                         QMessageBox.Ok)
                    logger.debug('[MLC_GUI] [LOAD_GUI] - Workspace was not set. Aborting program')
                    self.close()
                    sys.exit(0)
                else:
                    self._create_gui_config_from_scratch(config_filepath, workspace_dir)
                    QMessageBox.information(self, 'MLC Manager',
                                            'Workspace was succesfully set',
                                            QMessageBox.Ok)
                    logger.debug('[MLC_GUI] [LOAD_GUI] - Workspace was succesfully set: {0}'.format(workspace_dir))
            else:
                QMessageBox.critical(self, 'MLC Manager',
                                     'Workspace has not been set. Aborting program',
                                     QMessageBox.Ok)
                logger.debug('[MLC_GUI] [LOAD_GUI] - Workspace was not set. Aborting program')
                self.close()
                sys.exit(0)

        # Load GUI config
        self._gui_config = ConfigParser.ConfigParser()
        self._gui_config.read(config_filepath)
        workspace_dir = self._gui_config.get('MAIN', 'workspace')

        # Create the MLC Local instance and initialize the Experiments_Manager
        self._mlc_local = MLCLocal(workspace_dir)
        self._experiments_manager = ExperimentsManager(self._mlc_local, self._gui_config)
        logger.info('[MLC_GUI] Workspace directory: {0}'.format(self._gui_config.get('MAIN', 'workspace')))

    def get_gui_config(self):
        """
        This method MUST BE called after load_gui_config
        """
        return self._gui_config

    def edit_gui_config(self):
        # Create the properties Dialog with the MLC Manager Options
        dialog = QDialog()
        properties_dialog = Ui_PropertiesDialog()
        properties_dialog.setupUi(dialog)

        # Fill the TableView with the GUI Config file
        header = ['Parameter', 'Section', 'Value']
        table_model = ConfigParserTableModel("MLC MANAGER PARAMS", self._gui_config, header, self)
        properties_dialog.tableView.setModel(table_model)
        properties_dialog.tableView.resizeColumnsToContents()
        properties_dialog.tableView.setSortingEnabled(True)
        dialog.exec_()

    def on_experiment_list_clicked(self, model_index):
        list_view = self._autogenerated_object.experiment_list
        experiment_name = list_view.model().itemFromIndex(model_index).text()
        self._refresh_experiment_description(experiment_name)

    def _create_gui_config_from_scratch(self, config_filepath, workspace_dir):
        self._gui_config = ConfigParser.ConfigParser()
        self._gui_config.add_section('MAIN')
        self._gui_config.set('MAIN', 'workspace', workspace_dir)
        self._gui_config.add_section('WEB_SERVICE')
        self._gui_config.set('WEB_SERVICE', 'port', MLC_GUI.WEBSERVICE_PORT)
        with open(config_filepath, 'w') as cfg:
            self._gui_config.write(cfg)

    def load_and_refresh_experiment_info(self, experiment_name):

        self._experiments_manager.load_experiment_info(experiment_name)
        self._refresh_experiment_list_view()
        self._refresh_experiment_description(experiment_name)

    def load_and_refresh_experiments_info(self):
        # Clean the experiment list before filling it
        self._experiments_manager.load_experiments_info()
        self._refresh_experiment_list_view()

    def _refresh_experiment_list_view(self):
        list_view = self._autogenerated_object.experiment_list
        list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStandardItemModel(list_view)

        for experiment in self._experiments_manager.get_experiment_list():
            item = QStandardItem(experiment)
            model.appendRow(item)

        list_view.setModel(model)

    def _refresh_experiment_description(self, experiment_name):
        # Store the experiment selected to operate with it later
        self._experiment_selected = experiment_name
        experiment_description = self._experiments_manager.get_experiment_info(experiment_name)
        self._autogenerated_object.experiment_description.setHtml(experiment_description)

    def _clean_experiment_selection(self):
        """
        Call this method when an action that lose focus of the experiment list happens. For example,
        when a new project is created after pressing a buttons
        """
        self._experiment_selected = None
        self._autogenerated_object.experiment_description.setHtml("")


def main():
    app = QApplication(sys.argv)
    main_window = MLC_GUI()

    # Check if the workspace was already set
    main_window.load_gui_config()

    # Load the projects founded in the workspace
    main_window.load_and_refresh_experiments_info()

    # Object which manipulates MLC experiments
    # TODO: Replace this for WebService Architecture
    config = main_window.get_gui_config()

    # Init PyQt mainloop
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
