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

import logging
import logging.config
import platform
import os

os_platform = platform.system()
log_file = os.path.join(*[os.path.dirname(os.path.realpath(__file__)),
                          "..",
                          "..",
                          "conf",
                          "logging.{0}.conf".format(os_platform.lower())])

if os.path.isfile(log_file):
    print "Platform {0} is not supported. Using default logging file.".format(os_platform)
    log_file = os.path.join(*[os.path.dirname(os.path.realpath(__file__)),
                              "..",
                              "..",
                              "conf",
                              "logging.default.conf"])
print log_file
logger_ = None
logging.config.fileConfig(log_file)


def set_logger(mode):
    if (mode == "console" or
        mode == "testing" or
        mode == "root" or
        mode == "file"):

        global logger_
        logger_ = logging.getLogger(mode)


def get_gui_logger():
    return logging.getLogger("gui")
