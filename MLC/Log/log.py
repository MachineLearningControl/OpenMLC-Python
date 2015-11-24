import logging
import logging.config
import os

global logger
logger = logging.getLogger("default")

logging.config.fileConfig(os.path.dirname(os.path.realpath(__file__)) +
                          "/../../conf/logging.conf")


def set_logger(mode):
    if mode == "default" or mode == "testing":
        global logger
        logger = logging.getLogger(mode)
