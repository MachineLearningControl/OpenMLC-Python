from MixedRampedGauss import MixedRampedGauss
from MLC.Log.log import logger
import sys


class CreationFactory(object):
    @staticmethod
    def make(eng, config, strategy):
        if strategy == "mixed_ramped_gauss":
            return MixedRampedGauss(eng, config)
        else:
            logger.error("Evaluation method " + strategy +
                         " is not valid. "
                         "Aborting program")
            sys.exit(-1)
