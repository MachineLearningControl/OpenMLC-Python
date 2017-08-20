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

from __future__ import unicode_literals
import os
import matplotlib
import random
import sys

from matplotlib.figure import Figure
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtWidgets

from MLC.GUI.Experiment.MatplotlibCanvas.MplCanvas import MplCanvas


class CostPerIndividualCanvas(MplCanvas):

    def __init__(self, parent, width, height, dpi):
        MplCanvas.__init__(self, parent, width, height, dpi)
        self._costs = None

    def set_costs(self, costs):
        self._costs = costs

    def set_title(self, title):
        self._axes.set_title(title)

    def set_xlabel(self, text):
        self._axes.set_xlabel(text)

    def set_ylabel(self, text):
        self._axes.set_ylabel(text)

    def compute_initial_figure(self, log=False):
        x_axis = range(1, 101)
        if log:
            self._axes.semilogy(x_axis, self._costs)
        else:
            self._axes.plot(x_axis, self._costs)
