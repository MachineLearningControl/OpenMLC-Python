from PyQt5.QtChart import QChart, QChartView, QLineSeries, QSplineSeries
from PyQt5.QtChart import QValueAxis
from PyQt5.QtChart import QLogValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF, QPainter

import numpy as np


class QtChartWrapper():

    def __init__(self, chart_view=None, chart=None):
        self._ncurves = 0
        if chart:
            self._chart = chart
        else:
            self._chart = QChart()
            self._chart.legend().hide()

        if chart_view:
            self._view = chart_view
        else:
            self._view = QChartView(self._chart)
            self._view.setRenderHint(QPainter.Antialiasing)
            self._view.setUpdatesEnabled(True)

        self._xaxis = QValueAxis()
        self._yaxis = QValueAxis()

        # Save the curves in order to add data to them later
        self._curves = []

    def set_title(self, title):
        self._chart.setTitle(title)

    def set_object_name(self, name):
        self._view.setObjectName(name)

    def set_xaxis(self, log=False, label="", label_format="", tick_count=None):
        self._xaxis = self._create_axis(log, label, label_format, tick_count)
        self._chart.addAxis(self._xaxis, Qt.AlignBottom)

    def set_yaxis(self, log=False, label="", label_format="", tick_count=None):
        self._yaxis = self._create_axis(log, label, label_format, tick_count=None)
        self._chart.addAxis(self._yaxis, Qt.AlignLeft)

    def _create_axis(self, log, label, label_format, tick_count):
        axis = QValueAxis() if log == False else QLogValueAxis()
        axis.setTitleText(label)
        axis.setLabelFormat(label_format)

        if tick_count and not log:
            axis.setTickCount(tick_count)

        return axis

    def add_data(self, xdata, ydata, line_width=.1, color=None):
        # curve = QLineSeries()
        curve = QSplineSeries()
        pen = curve.pen()

        if color is not None:
            pen.setColor(color)

        pen.setWidthF(line_width)
        curve.setPen(pen)
        curve.setUseOpenGL(True)
        # curve.append(self._series_to_polyline(xdata, ydata))

        # Convert the xdata and ydata into a list of points. Add them to the curve
        points = []
        for i in xrange(0, len(xdata)):
            points.append(QPointF(xdata[i], ydata[i]))
        curve.append(points)

        self._chart.addSeries(curve)
        self._curves.append(curve)
        self._ncurves += 1

        curve.attachAxis(self._xaxis)
        curve.attachAxis(self._yaxis)
        return self._ncurves - 1

    def add_curve(self, line_width=.1, color=None):
        curve = QSplineSeries()
        pen = curve.pen()

        if color is not None:
            pen.setColor(color)

        pen.setWidthF(line_width)
        curve.setPen(pen)
        curve.setUseOpenGL(True)

        self._chart.addSeries(curve)
        self._curves.append(curve)
        self._ncurves += 1

        curve.attachAxis(self._xaxis)
        curve.attachAxis(self._yaxis)
        return self._ncurves - 1

    def append_point(self, curve_number, x, y):
        # FIXME: Do something different to uniquely identify the curve.
        # The curve number it is not enough
        try:
            self._curves[curve_number].append(QPointF(x, y))
            return True
        except IndexError:
            return False

    def get_widget(self):
        """
        Return the widget to be added to the GUI
        """
        return self._view

    def repaint(self):
        self._view.repaint()

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
