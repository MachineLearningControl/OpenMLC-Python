from MLC.GUI.Tables.ConfigTableModel import ConfigTableModel
from MLC.Log.log import get_gui_logger
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox

logger = get_gui_logger()

class FirstIndividualsTabView(QObject):

    def __init__(self, experiment_name, parent, autogen_object):
        QObject.__init__(self, parent)
        self._experiment_name = experiment_name
        self._parent = parent
        self._autogen_object = autogen_object
        self._first_indivs_table = self._autogen_object.first_indivs_table

    def individual_added(self, indiv_list, err_msg):
        if not indiv_list:
            QMessageBox.critical(self._parent, "Error adding Individual", err_msg)
            return

        QMessageBox.information(self._parent, "Individual added",
                                "Individual {0} was succesfully added"
                                .format(indiv_list[-1]))
        logger.info("[FIRST_INDIVS_MANAGER] Experiment {0} - "
                    "Individual {1} was succesfully added"
                    .format(self._experiment_name, indiv_list[-1]))
        self._load_table(indiv_list)

    def individual_removed(self, indiv_list, err_msg):
        pass

    def individual_modified(self, indiv_list, err_msg):
        pass

    def _load_table(self, indivs):
        header = ['Index', 'Value']

        # Generate the dict to be used by the Table Model
        indivs_list = []
        for index in xrange(len(indivs)):
            indivs_list.append([index + 1, indivs[index]])

        table_model = ConfigTableModel(name="FIRST INDIVS TABLE",
                                       data=indivs_list,
                                       header=header,
                                       parent=self._parent)

        self._first_indivs_table.setModel(table_model)
        self._first_indivs_table.setDisabled(False)
        self._first_indivs_table.setVisible(False)
        self._first_indivs_table.resizeColumnsToContents()
        self._first_indivs_table.setVisible(True)
        self._first_indivs_table.setSortingEnabled(True)
