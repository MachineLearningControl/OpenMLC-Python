from MLC.mlc_parameters.mlc_parameters import Config
from MLC.config import get_test_path

import os


class TestHelper:
    DEFAULT_CONF_FILENAME = "default_test_configuration.ini"

    @staticmethod
    def load_default_configuration():
        Config.get_instance().read(os.path.join(get_test_path(),
                                                TestHelper.DEFAULT_CONF_FILENAME))
