import MLC.Log.log as lg
import importlib
import sys

from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Population.Evaluation.StandaloneEvaluator import StandaloneEvaluator


class EvaluatorFactory(object):
    @staticmethod
    def get_callback():
        function_name = Config.get_instance().get('EVALUATOR', 'evaluation_function')
        module_name = 'Evaluation.{0}'.format(function_name)

        try:
            # WARNING: I am unloading manually the evaluation function module. I need to do this
            # because Python does not support module unloading and my evaluation functions are
            # all the same, so when one experiment loads his module, other project with the same
            # name of module won't be able to load yours
            ev_module = sys.modules["Evaluation"]
            del sys.modules['Evaluation']
            del ev_module
            lg.logger_.debug("[EV_FACTORY] Module {0} was removed".format(sys.modules["Evaluation"]))
        except KeyError, err:
            # If the module cannot be unload because it does not exists, continue
            pass

        lg.logger_.debug('[EV_FACTORY] Importing module {0}'.format(module_name))
        try:
            # lg.logger_.debug("[EV_FACTORY] Sys.path: {0}".format(sys.path))
            module = importlib.import_module(module_name)
            reload(module)
            return module
        except ImportError, err:
            lg.logger_.debug("[EV_FACTORY] Evaluation function doesn't exists. "
                             "Aborting program. Error Msg: {0}".format(err))
            sys.exit(-1)

    @staticmethod
    def make(strategy, callback_manager):
        if strategy == "mfile_standalone":
            ev_callback = EvaluatorFactory.get_callback()
            return StandaloneEvaluator(ev_callback, callback_manager)
        else:
            lg.logger_.error("[EV_FACTORY] Evaluation method " +
                             strategy + " is not valid. Aborting program")
            sys.exit(-1)
