import logging
import logging.config
import os

logger_ = None
logging.config.fileConfig(os.path.dirname(os.path.realpath(__file__)) +
                          "/../../conf/logging.conf")


def set_logger(mode):
    if mode == "default" or mode == "testing" or mode == "root":
        global logger_
        logger_ = logging.getLogger(mode)
