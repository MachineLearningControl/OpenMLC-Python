from MixedRampedGauss import MixedRampedGauss
import logging
import sys


class CreationFactory(object):
    @staticmethod
    def make(strategy):
        if strategy == "MixedRampedGauss":
            return MixedRampedGauss()
        else:
            logging.getLogger("default").error("Evaluation method "
                                               "inserted is not valid. "
                                               "Aborting program")
            sys.exit(-1)
