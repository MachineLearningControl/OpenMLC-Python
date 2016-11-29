import MLC.Log.log as lg
import importlib
import sys

from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Population.Evaluation.StandaloneEvaluator import StandaloneEvaluator


class EvaluatorFactory(object):
    @staticmethod
    def get_callback():
        module_name = Config.get_instance().get('EVALUATOR', 'evaluation_function')
        lg.logger_.debug('[EV_FACTORY] Importing module {0}'.format(module_name))
        try:
            callback = importlib.import_module('MLC.Scripts.Evaluation.' + module_name)
            return callback
        except ImportError:
            lg.logger_.debug("[EV_FACTORY] Evaluation function doesn't exists. " +
                             "Aborting program...")
            sys.exit(-1)

    @staticmethod
    def make(strategy, on_evaluate_callback):
        if strategy == "mfile_standalone":
            ev_callback = EvaluatorFactory.get_callback()
            return StandaloneEvaluator(ev_callback, on_evaluate_callback)
        else:
            lg.logger_.error("[EV_FACTORY] Evaluation method " +
                             strategy + " is not valid. Aborting program")
            sys.exit(-1)
