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
            function_name = Config.get_instance().get('EVALUATOR', 'preev_function')
            module_name = "Preevaluation.{0}".format(function_name)

            try:
                # WARNING: I am unloading manually the evaluation function module. I need to do this
                # because Python does not support module unloading and my evaluation functions are
                # all the same, so when one experiment loads his module, other project with the same
                # name of module won't be able to load yours
                preev_module = sys.modules["Preevaluation"]
                del sys.modules['Preevaluation']
                del preev_module
                lg.logger_.debug("[EV_FACTORY] Module {0} was removed"
                                 .format(sys.modules["Preevaluation"]))
            except KeyError, err:
                # If the module cannot be unload because it does not exists, continue
                pass

            lg.logger_.debug('[PREEV_MANAGER] Importing module {0}'.format(module_name))
            try:
                module = importlib.import_module(module_name)
                reload(module)
                return module
            except ImportError:
                lg.logger_.debug("[PREEV_MANAGER] Preevaluation function doesn't exists. " +
                                 "Aborting program...")
                sys.exit(-1)


