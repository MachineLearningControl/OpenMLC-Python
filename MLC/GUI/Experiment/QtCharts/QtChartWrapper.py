from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtChart import QValueAxis
from PyQt5.QtChart import QLogValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPolygonF, QPainter

import numpy as np


class QtChartWrapper():

    def __init__(self):
        self._ncurves = 0
        self._chart = QChart()
        self._chart.legend().hide()
        self._view = QChartView(self._chart)
        self._view.setRenderHint(QPainter.Antialiasing)

        # By default, create
        self._xaxis = QValueAxis()
        self._yaxis = QValueAxis()

    def _series_to_polyline(self, xdata, ydata):
        """Convert series data to QPolygon(F) polyline

        This code is derived from PythonQwt's function named
        `qwt.plot_curve.series_to_polyline`"""
        size = len(xdata)
        polyline = QPolygonF(size)
        pointer = polyline.data()
        dtype, tinfo = np.float, np.finfo  # integers: = np.int, np.iinfo
        pointer.setsize(2 * polyline.size() * tinfo(dtype).dtype.itemsize)
        memory = np.frombuffer(pointer, dtype)
        memory[:(size - 1) * 2 + 1:2] = xdata
        memory[1:(size - 1) * 2 + 2:2] = ydata
        return polyline

    def set_title(self, title):
        self._chart.setTitle(title)

    def set_xaxis(self, log=False, label="", label_format="", tick_count=None):
        self._xaxis = self._create_axis(log, label, label_format, tick_count)
        self._chart.addAxis(self._xaxis, Qt.AlignBottom)

    def set_yaxis(self, log=False, label="", label_format="", tick_count=None):
        self._yaxis = self._create_axis(log, label, label_format, tick_count)
        self._chart.addAxis(self._yaxis, Qt.AlignLeft)

    def _create_axis(self, log, label, label_format, tick_count):
        axis = QValueAxis() if log == False else QLogValueAxis()
        axis.setTitleText(label)
        axis.setLabelFormat(label_format)

        if tick_count:
            axis.setTickCount(tick_count)

        return axis

    def add_data(self, xdata, ydata, color=None):
        curve = QLineSeries()
        pen = curve.pen()

        if color is not None:
            pen.setColor(color)

        pen.setWidthF(.1)
        curve.setPen(pen)
        curve.setUseOpenGL(True)
        curve.append(self._series_to_polyline(xdata, ydata))
        self._chart.addSeries(curve)
        self._ncurves += 1

        curve.attachAxis(self._xaxis)
        curve.attachAxis(self._yaxis)

    def get_widget(self):
        """
        Return the widget to be added to the GUI
        """
        return self._view
