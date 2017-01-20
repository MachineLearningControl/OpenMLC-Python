from MLC.GUI.Experiment.QtCharts.QtChartWrapper import QtChartWrapper
from MLC.mlc_parameters.mlc_parameters import Config
from PyQt5.QtCore import Qt


class GenealogyChart(QtChartWrapper):
    CHART_COLORS = [Qt.black, Qt.red, Qt.green, Qt.blue,
                    Qt.cyan, Qt.magenta, Qt.yellow, Qt.gray]

    def __init__(self, mlc_local, generation, individual):
        QtChartWrapper.__init__(self, False)
        self._mlc_local = mlc_local
        self._indivs_per_gen = Config.get_instance().getint("POPULATION", "size")
        self._amount_generations = generation
        self._indiv_index = individual

        self._add_axis()
        self._add_swimming_lines()

    def _add_axis(self):
        # Set the object name to be able to retrieve it later
        self.set_xaxis(log=False, label="Generations",
                       label_format='%i', tick_count=self._amount_generations)
        self.set_yaxis(log=False, label="Individuals",
                       label_format='%g', tick_count=10)

        chart_view = self.get_widget()
        chart_view.chart().axisX().setRange(1, self._amount_generations)
        chart_view.chart().axisY().setRange(1, self._indivs_per_gen)

    def _add_swimming_lines(self):
        amount_colors = len(GenealogyChart.CHART_COLORS)
        # TODO: Increase the marker size
        # when the individuals amount per generations decrease
        marker_size = 3

        for index in xrange(self._amount_generations + 1):
            self.add_scatter(marker_size=marker_size,
                             color=GenealogyChart.CHART_COLORS[index % amount_colors])

            for indiv_id in xrange(self._indivs_per_gen):
                self.append_point(index, index, indiv_id)
