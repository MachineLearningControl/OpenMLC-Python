import logging
import logging.config

global logger
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("default")