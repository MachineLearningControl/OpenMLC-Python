from MixedRampedGauss import MixedRampedGauss
import MLC.Log.log as lg
import sys


class CreationFactory(object):
    @staticmethod
    def make(strategy):
        if strategy == "mixed_ramped_gauss":
            return MixedRampedGauss()
        else:
            lg.logger_.error("[CREATION_FACTORY] Evaluation method " +
                             strategy + " is not valid. Aborting program")
            sys.exit(-1)
