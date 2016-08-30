import MLC.Log.log as lg
import sys
from MLC.mlc_parameters.mlc_parameters import Config

"""
Class that store the preevaluation methods availables and used to call them
"""


class PreevaluationManager(object):
    callback = {}

    @staticmethod
    def set_callback(callback_name, ev_callback):
        PreevaluationManager.callback[callback_name] = ev_callback

    @staticmethod
    def get_callback():
        """
        @brief  Gets the preevaluation callback
        @return None if no functions was loaded to MLC. The callback in other case
        """
        # Check if the preevaluation is activated
        if Config.get_instance().getboolean('EVALUATOR', 'preevaluation'):
            callback_name = Config.get_instance().get('EVALUATOR', 'preev_function')
            try:
                return PreevaluationManager.callback[callback_name]
            except KeyError:
                lg.logger_.debug("Preevaluation function doesn't exists. Aborting program...")

        return None
