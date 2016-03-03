import logging
import logging.config
import os

logger_ = None
logging.config.fileConfig(os.path.dirname(os.path.realpath(__file__)) +
                          "/../../conf/logging.conf")


def set_logger(mode):
    if mode == "console" or mode == "testing" or \
       mode == "root" or mode == "file":
        global logger_
        logger_ = logging.getLogger(mode)
