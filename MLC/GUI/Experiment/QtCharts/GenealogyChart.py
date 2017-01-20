import time

from MLC.GUI.Experiment.QtCharts.QtChartWrapper import QtChartWrapper
from MLC.mlc_parameters.mlc_parameters import Config
from PyQt5.QtCore import Qt


class GenealogyChart(QtChartWrapper):
    SWIM_LINE_COLORS = [Qt.cyan, Qt.magenta, Qt.gray, Qt.yellow]
    INDIV_COLORS = [Qt.black, Qt.red, Qt.green, Qt.blue]

    def __init__(self, mlc_local, experiment_name, generation, individual):
        QtChartWrapper.__init__(self, False)
        self._mlc_local = mlc_local
        self._indivs_per_gen = Config.get_instance().getint("POPULATION", "size")
        self._amount_generations = generation
        self._indiv_index = individual
        self._experiment_name = experiment_name
        self._next_curve = self._amount_generations

        self._add_axis()
        self._add_swimming_lines()
        self._add_individuals()

    def _add_axis(self):
        # Set the object name to be able to retrieve it later
        self.set_xaxis(log=False, label="Generations",
                       label_format='%i', tick_count=self._amount_generations)
        self.set_yaxis(log=False, label="Individuals",
                       label_format='%g', tick_count=10)

        chart_view = self.get_widget()
        chart_view.chart().axisX().setRange(0.5, self._amount_generations + 0.5)
        chart_view.chart().axisY().setRange(1, self._indivs_per_gen)

    def _add_swimming_lines(self):
        amount_colors = len(GenealogyChart.SWIM_LINE_COLORS)
        # TODO: Increase the marker size
        # when the individuals amount per generations decrease
        marker_size = 3

        for index in xrange(self._amount_generations + 1):
            self.add_scatter(marker_size=marker_size,
                             color=GenealogyChart.SWIM_LINE_COLORS[index % amount_colors])

            for indiv_id in xrange(self._indivs_per_gen):
                self.append_point(index, index, indiv_id)

    def _add_individuals(self):
        start_time = time.time()
        generations = [self._mlc_local.get_generation(self._experiment_name, i)
                       for i in xrange(1, self._amount_generations + 1)]

        gen_method_points = [[], [], [], []]
        indivs_to_process = []
        new_indivs_to_process = [self._indiv_index]

        for gen in xrange(self._amount_generations - 1, -1, -1):
            indivs_to_process = new_indivs_to_process
            new_indivs_to_process = []

            for indiv_id in indivs_to_process:
                gen_method = generations[gen].get_gen_methods()[indiv_id - 1]

                if gen != 0:
                    parents = generations[gen].get_parents()[indiv_id - 1]
                    if type(parents) == list:
                        for parent_index in range(len(parents)):
                            new_indivs_to_process.append(parents[parent_index])
                            self.add_line_curve(line_width=.3, color=GenealogyChart.INDIV_COLORS[gen_method - 1])
                            self.append_point(self._next_curve, gen + 1, indiv_id)
                            self.append_point(self._next_curve, gen, parents[parent_index])
                            self._next_curve += 1
                    else:
                        new_indivs_to_process.append(parents)
                        self.add_line_curve(line_width=.3, color=GenealogyChart.INDIV_COLORS[gen_method - 1])
                        self.append_point(self._next_curve, gen + 1, indiv_id)
                        self.append_point(self._next_curve, gen, parents[parent_index])
                        self._next_curve += 1

        elapsed_time = time.time() - start_time
        print elapsed_time
