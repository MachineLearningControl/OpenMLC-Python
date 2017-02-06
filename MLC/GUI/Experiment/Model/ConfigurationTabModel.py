from MLC.GUI.Common.Observer import Observer

class ConfigurationTabModel(object):

    def __init__(self, experiment_name, mlc_local):
        self._experiment_name = experiment_name
        self._mlc_local = mlc_local
        self._individuals = []
        self._individuals_observer = Observer()

    def register_observer_when_individual_list_change(self, observer):
        self._individuals_observer.register(observer)

    def add_individual(self, indiv_value):
        pass
