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

# -*- coding: utf-8 -*-
import time

from MLC.GUI.Experiment.QtCharts.QtChartWrapper import QtChartWrapper
from MLC.Log.log import get_gui_logger
from MLC.mlc_parameters.mlc_parameters import Config
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont

logger = get_gui_logger()


class GenealogyChart(QtChartWrapper):
    SWIM_LINE_COLORS = [QColor(159, 202, 230),
                        QColor(241, 190, 169),
                        QColor(244, 206, 116),
                        QColor(174, 125, 184),
                        QColor(119, 172, 48),
                        QColor(121, 206, 242),
                        QColor(220, 167, 177)]

    INDIV_COLORS = [Qt.blue, Qt.red, Qt.black, Qt.darkYellow]
    INDIV_LEGEND = ["Replication", "Mutation", "Crossover", "Elitism"]

    def __init__(self, mlc_local, experiment_name, generation, individual):
        QtChartWrapper.__init__(self, show_legend=True)
        self._mlc_local = mlc_local
        self._indivs_per_gen = Config.get_instance().getint("POPULATION", "size")
        self._amount_generations = generation
        self._indiv_index = individual
        self._experiment_name = experiment_name
        self._next_curve = self._amount_generations

        self._add_axis()
        self._add_swimming_lines()
        self._add_individuals()
        self._add_title()
        self._add_legend_markers()

    def _add_legend_markers(self):
        legend = self.get_legend()
        # Hide all the legend of the Series added to this moment
        for legend_marker in legend.markers():
            legend_marker.setVisible(False)

        # Add the evolution strategies as four empty curve in order to set the
        # graphic legend
        for index in range(len(GenealogyChart.INDIV_COLORS)):
            self.add_line_curve(line_width=.7,
                                color=GenealogyChart.INDIV_COLORS[index],
                                legend=GenealogyChart.INDIV_LEGEND[index])

    def _add_title(self):
        chart_title = 'Generation N°{0} - Individual N°{1}'.format(self._amount_generations,
                                                                   self._indiv_index)
        chart_font = QFont()
        chart_font.setWeight(QFont.ExtraBold)
        self.set_title(chart_title, chart_font)

    def _add_axis(self):
        # Set the object name to be able to retrieve it later
        self.set_xaxis(log=False, label="Generations",
                       label_format='%i', tick_count=self._amount_generations)
        self.set_yaxis(log=False, label="Individuals",
                       label_format='%g', tick_count=10)

        chart_view = self.get_widget()
        chart_view.chart().axisX().setRange(0.9, self._amount_generations + 0.1)
        chart_view.chart().axisY().setRange(0, self._indivs_per_gen)
        chart_view.chart().axisX().setGridLineVisible(False)
        chart_view.chart().axisY().setGridLineVisible(False)

    def _add_swimming_lines(self):
        amount_colors = len(GenealogyChart.SWIM_LINE_COLORS)
        # TODO: Increase the marker size
        # when the individuals amount per generations decrease
        marker_size = 4

        for index in range(self._amount_generations):
            self.add_scatter(marker_size=marker_size,
                             color=GenealogyChart.SWIM_LINE_COLORS[(index - 1) % amount_colors])

            for indiv_id in range(1, self._indivs_per_gen + 1):
                self.append_point(index, index + 1, indiv_id)

    def _add_individuals(self):
        logger.debug("[GENEALOGY_CHART] Looping through individuals")
        start_time = time.time()
        generations = [self._mlc_local.get_generation(self._experiment_name, i)
                       for i in range(1, self._amount_generations + 1)]

        indivs_to_process = []
        new_indivs_to_process = [self._indiv_index]

        for gen in range(self._amount_generations - 1, -1, -1):
            indivs_to_process = new_indivs_to_process
            new_indivs_to_process = []

            for indiv_id in indivs_to_process:
                gen_method = generations[gen].get_gen_methods()[indiv_id - 1]

                if gen != 0:
                    parents = generations[gen].get_parents()[indiv_id - 1]
                    for parent_index in range(len(parents)):
                        new_indivs_to_process.append(parents[parent_index])
                        self.add_line_curve(line_width=2,
                                            color=GenealogyChart.INDIV_COLORS[gen_method - 1])
                        self.append_point(self._next_curve, gen + 1, indiv_id)
                        self.append_point(self._next_curve, gen, parents[parent_index])
                        self._next_curve += 1

        elapsed_time = time.time() - start_time
        logger.debug("[GENEALOGY_CHART] Individuals added to chart. Time elapsed: {0}"
                     .format(elapsed_time))
