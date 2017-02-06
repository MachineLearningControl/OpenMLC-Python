from MLC.GUI.Common.Observer import Observer
from MLC.GUI.Experiment.Model.util import check_individual_value
from MLC.Log.log import get_gui_logger
from MLC.mlc_parameters.mlc_parameters import Config

logger = get_gui_logger()


class FirstIndividualsTabModel(object):

    def __init__(self, experiment_name, mlc_local):
        self._experiment_name = experiment_name
        self._mlc_local = mlc_local
        self._individuals = []
        self._add_individual_observer = Observer()
        self._modify_individual_observer = Observer()
        self._remove_individual_observer = Observer()

    def register_observer_add_individual(self, observer):
        self._add_individual_observer.register(observer)

    def register_observer_modify_individual(self, observer):
        self._modify_individual_observer.register(observer)

    def register_observer_remove_individual(self, observer):
        self._remove_individual_observer.register(observer)

    def add_individual(self, indiv_value):
        """
        Return true if the individual was well-formed
        """
        result, err = check_individual_value(experiment_name=self._experiment_name,
                                             log_prefix="[FIRST_INDIVS_MANAGER]",
                                             indiv_value=indiv_value)
        if result:
            self._individuals.append(indiv_value)
            self._add_individual_observer.notify(indiv_list=self._individuals,
                                                 err_msg=None)
            return True

        self._add_individual_observer.notify(indiv_list=None,
                                             err_msg=err)
        return False

    def modify_individual(self, index, indiv_value):
        try:
            # Get the individual, so we can check if it exists
            indiv = self._individuals[index]
        except IndexError, err:
            err_string = ("[FIRST_INDIVS] Individual index does not exists. "
                          "Index: {0}".format(index))
            logger.error(err_string)

    def remove_individual(self, index):
        """
        Return true if the individual was succesfully removed
        """
        try:
            indiv = self._individuals[index]
            del self._individuals[index]
            logger.info("[FIRST_INDIVS] Indiv (Index: {0}, Value: {1}) was succesfully removed"
                        .format(index, indiv))
            self._remove_individual_observer.notify(indiv_list=self._individuals,
                                                    err_msg=None)
            return True
        except IndexError, err:
            err_string = ("[FIRST_INDIVS] Individual index does not exists. "
                          "Index: {0}".format(index))
            logger.error(err_string)

        return False
