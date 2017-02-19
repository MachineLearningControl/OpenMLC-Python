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

import operator

from MLC.Log.log import get_gui_logger
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import pyqtSignal
import datetime

logger = get_gui_logger()


class ConfigTableModel(QAbstractTableModel):

    def __init__(self, name, data, header, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self._name = name
        self._header = header
        self._data = data
        self._editable_columns = []

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        try:
            return len(self._data[0])
        except IndexError:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()

        return QVariant(self._data[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._header[col])

    def sort(self, n_col, order):
        """
        Sort table by given column number.
        """
        self.layoutAboutToBeChanged.emit()
        self._data = sorted(self._data, key=operator.itemgetter(n_col))
        if order == Qt.DescendingOrder:
            self._data.reverse()

        self.layoutChanged.emit()

    def set_editable_columns(self, editable_columns):
        """
        List of columns that can be edited
        """
        self._editable_columns = editable_columns

    def sort_by_col(self, col_number, descending=False):
        if descending:
            self.sort(col_number, Qt.DescendingOrder)
        else:
            self.sort(col_number, Qt.AscendingOrder)

    def flags(self, index):
        if index.column() in self._editable_columns:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            if self._data[index.row()][index.column()] != value:
                logger.debug("[TABLE_VIEW] [{0}] Value changed. Row: {1} - Col: {2}"
                             .format(self._name, index.row(), index.column()))
                self.layoutAboutToBeChanged.emit()
                self._data[index.row()][index.column()] = value
                self.layoutChanged.emit()

                # FIXME: I believe that this callback is used to report a change in a sector of the table.
                # That's why it has two QModelIndex in its firm. We are just using it to report the change
                # in a cell, so that's why I repeat the cell modified twice in the method's firm
                self.dataChanged.emit(index, index)
                return True
            else:
                logger.debug("[TABLE_VIEW] [{0}] Value changed to the same value stored. "
                             "Don't emit any signal. Row: {1} - Col: {2}"
                             .format(self._name, index.row(), index.column()))
        return False

    def set_data(self, row, col, value):
        try:
            # Check if the row exists, indexing the element to modify
            self.layoutAboutToBeChanged.emit()
            self._data[row][col] = value
            self.layoutChanged.emit()
        except IndexError:
            logger.error("[TABLE_VIEW] [{0}] - [SET_DATA] IndexError while retrieving data. "
                         "Row: {1} - Col: {2}"
                         .format(self._name, index.row(), index.column()))

    def get_data(self, row, col):
        try:
            return self._data[row][col]
        except IndexError:
            logger.error("[TABLE_VIEW] [{0}] - [GET_DATA] IndexError while retrieving data. "
                         "Row: {1} - Col: {2}"
                         .format(self._name, index.row(), index.column()))
            return None

    def set_data_changed_callback(self, callback):
        self.dataChanged.connect(callback)
