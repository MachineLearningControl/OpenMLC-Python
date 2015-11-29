from MLC.Population.Evaluation.StandaloneEvaluator import StandaloneEvaluator
import MLC.Log.log as lg
import sys


class EvaluatorFactory(object):
    @staticmethod
    def make(eng, config, strategy):
        if strategy == "mfile_standalone":
            return StandaloneEvaluator(eng, config)
        else:
            lg.logger_.error("[CREATION_FACTORY] Evaluation method " +
                             strategy + " is not valid. Aborting program")
            sys.exit(-1)
