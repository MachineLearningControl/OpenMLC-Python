import operator

from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QVariant


class ConfigParserTableModel(QAbstractTableModel):

    def __init__(self, config_parser, header, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self.data = self._config_parser_to_list_of_lists(config_parser)

    def _config_parser_to_list_of_lists(self, config_parser):
        data = []
        for each_section in config_parser.sections():
            for (each_key, each_val) in config_parser.items(each_section):
                data.append([each_key, each_section, each_val])
        return data

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.data[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.data[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.header[col])

    def sort(self, n_col, order):
        """Sort table by given column number.
        """
        self.data = sorted(self.data, key=operator.itemgetter(n_col))
        if order == Qt.DescendingOrder:
            self.data.reverse()
