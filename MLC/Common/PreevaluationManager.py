import MLC.Log.log as lg
import importlib
import sys
from MLC.mlc_parameters.mlc_parameters import Config

"""
Class that store the preevaluation methods availables and used to call them
"""


class PreevaluationManager(object):

    @staticmethod
    def get_callback():
        """
        @brief  Gets the preevaluation callback
        @return None if no functions was loaded to MLC. The callback in other case
        """
        # Check if the preevaluation is activated
        if Config.get_instance().getboolean('EVALUATOR', 'preevaluation'):
            module_name = Config.get_instance().get('EVALUATOR', 'preev_function')
            lg.logger_.debug('[PREEV_MANAGER] Importing module {0}'.format(module_name))
            try:
                callback = importlib.import_module('MLC.Scripts.Preevaluation.' + module_name)
                return callback
            except ImportError:
                lg.logger_.debug("[PREEV_MANAGER] Preevaluation function doesn't exists. " +
                                 "Aborting program...")
                sys.exit(-1)


