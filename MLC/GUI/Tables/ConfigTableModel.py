import operator

from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import pyqtSignal


class ConfigTableModel(QAbstractTableModel):

    def __init__(self, config, header, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self._header = header
        self._data = config

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._data[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self._data[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._header[col])

    def sort(self, n_col, order):
        """Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self._data = sorted(self._data, key=operator.itemgetter(n_col))
        if order == Qt.DescendingOrder:
            self._data.reverse()

        self.layoutChanged.emit()

    def sort_by_section_in_descending_order(self):
        self.sort(1, Qt.AscendingOrder)
