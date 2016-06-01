"""
General MLC configuration, this functions return absolute paths to the MLC project folders.
This file should be placed on root_prohect/MLC/config.py
"""
import os


def get_mlc_root_directory():
    this_file = os.path.abspath(__file__)
    return os.path.dirname(os.path.join(os.path.dirname(this_file), "../"))


def get_src_path():
    """
    :return: absolute path to mlcv3 python code
    """
    return os.path.join(get_mlc_root_directory(), "MLC")


def get_config_path():
    """
    :return: absolute path to mlcv3 configuration directories (ini and conf files)
    """
    return os.path.join(get_mlc_root_directory(), "conf")


def get_tools_path():
    """
    :return: absolute path to mlcv3 general tools
     """
    return os.path.join(get_mlc_root_directory(), "tools")


def get_test_path():
    """
    :return: absolute path to mlcv3 tests (unittests and integration tests)
    """
    return os.path.join(get_mlc_root_directory(), "tests")


def get_matlab_path():
    """
    :return: absolute path to MLC matlab code
    """
    return os.path.join(get_mlc_root_directory(), "matlab_code")