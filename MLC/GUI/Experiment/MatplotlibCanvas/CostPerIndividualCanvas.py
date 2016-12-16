from __future__ import unicode_literals
import matplotlib
import os
import random
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        x_axis = xrange(1, 101)
        if log:
            self._axes.semilogy(x_axis, self._costs)
        else:
            self._axes.plot(x_axis, self._costs)
