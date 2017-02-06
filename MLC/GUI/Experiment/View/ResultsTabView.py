from PyQt5.QtCore import QObject


class ResultsTabView(QObject):

    def __init__(self, experiment_name, parent, autogen_object):
        QObject.__init__(self, parent)
        self._experiment_name = experiment_name
        self._parent = parent
        self._autogen_object = autogen_object
