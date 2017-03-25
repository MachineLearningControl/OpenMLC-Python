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

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtGui import QMovie
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from MLC.GUI.Autogenerated.autogenerated import Ui_ArduinoConnectionDialog

from MLC.GUI.Common.QtWaitingSpinner import QtWaitingSpinner
from MLC.GUI.Experiment.ArduinoConfigManager.Common import create_local_full_path


class ArduinoConnectionDialog(QDialog, QObject):
    signal_update = pyqtSignal()

    def __init__(self, parent=None):
        super(ArduinoConnectionDialog, self).__init__(parent)
        self.ui = Ui_ArduinoConnectionDialog()
        self.ui.setupUi(self)
        # Init status images
        self.__ok_tick = QPixmap()
        self.__ok_tick.load(create_local_full_path("images", "ok_b.png"))
        self.__ok_tick = self.__ok_tick.scaled(100, 100)
        self.__error_tick = QPixmap()
        self.__error_tick.load(create_local_full_path("images", "error.png"))
        self.__error_tick = self.__error_tick.scaled(100, 100)

        # Init loading spinner
        self.__spinner = QtWaitingSpinner(self.ui.widget)
        self.ui.verticalLayout_2.addWidget(self.__spinner)
        self.__label = QLabel()
        self.__spinner.start()
        # self.__spinner.setFileName(create_local_full_path("images", "connection.gif"))
        # self.__spinner = QtWaitingSpinner(self)
        # self.ui.loadingPanel.setMovie(self.movie)
        self.resize(150, 150)
        self.setFixedSize(self.size())  # Avoid Dialog resize
        self.__update_callback = self.__no_change
        self.signal_update.connect(self.handle_update)
        # self.set_ok()

    def __remove_spinner(self):
        self.ui.widget.layout().removeWidget(self.__spinner)
        # self.ui.verticalLayout_2.removeWidget(self.__spinner)

        if self.__spinner is not None:
            self.__spinner.deleteLater()
            self.__spinner = None

        self.ui.widget.layout().removeWidget(self.__label)

    def __no_change(self):
        return

    def __config_ok_tick(self):
        self.__remove_spinner()
        self.__label = QLabel(self.ui.widget)
        self.ui.verticalLayout_2.addWidget(self.__label)
        self.__label.setPixmap(self.__ok_tick)
        self.ui.status_label.setText("Succesfully connected!")
        self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

    def __config_error_tick(self):
        self.__remove_spinner()
        self.__label = QLabel(self.ui.widget)
        self.ui.verticalLayout_2.addWidget(self.__label)
        self.__label.setPixmap(self.__error_tick)
        self.ui.status_label.setText(self.__error)
        self.ui.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

    def set_ok(self):
        self.__update_callback = self.__config_ok_tick
        self.signal_update.emit()

    def set_error(self, msg):
        self.__update_callback = self.__config_error_tick
        self.__error = msg
        self.signal_update.emit()

    def handle_update(self):
        self.__update_callback()
