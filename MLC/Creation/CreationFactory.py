from MixedRampedGauss import MixedRampedGauss
import logging
import sys


class CreationFactory(object):
    @staticmethod
    def make(strategy):
        if strategy == "mixed_ramped_gauss":
            return MixedRampedGauss()
        else:
            logging.getLogger("default").error("Evaluation method " + strategy +
                                               " is not valid. "
                                               "Aborting program")
            sys.exit(-1)
