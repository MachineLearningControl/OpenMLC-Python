# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
General MLC configuration, this functions return absolute paths to the MLC
project folders.
This file should be placed on root_prohect/MLC/config.py
"""
import os
import __builtin__

__builtin__.working_directory = os.path.abspath(".")


def get_working_directory():
    return __builtin__.working_directory


def set_working_directory(new_working_dir):
    __builtin__.working_directory = new_working_dir


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
    :return: absolute path to mlcv3 configuration directories (ini and
        conf files)
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


def get_templates_path():
    """
    :return: absolute path to the templates folder
    """
    return os.path.join(get_mlc_root_directory(), "templates")
