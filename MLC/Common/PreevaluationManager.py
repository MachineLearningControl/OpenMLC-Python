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

import MLC.Log.log as lg
import importlib
import sys
from MLC.mlc_parameters.mlc_parameters import Config

"""
Class that store the preevaluation methods availables and used to call them
"""


class PreevaluationManager(object):

    @staticmethod
    def get_callback():
        """
        @brief  Gets the preevaluation callback
        @return None if no functions was loaded to MLC. The callback in other case
        """
        # Check if the preevaluation is activated
        if Config.get_instance().getboolean('EVALUATOR', 'preevaluation'):
            function_name = Config.get_instance().get('EVALUATOR', 'preev_function')
            module_name = "Preevaluation.{0}".format(function_name)

            try:
                # WARNING: I am unloading manually the evaluation function module. I need to do this
                # because Python does not support module unloading and my evaluation functions are
                # all the same, so when one experiment loads his module, other project with the same
                # name of module won't be able to load yours
                preev_module = sys.modules["Preevaluation"]
                del sys.modules['Preevaluation']
                del preev_module
                lg.logger_.debug("[EV_FACTORY] Module {0} was removed"
                                 .format(sys.modules["Preevaluation"]))
            except KeyError, err:
                # If the module cannot be unload because it does not exists, continue
                pass

            lg.logger_.debug('[PREEV_MANAGER] Importing module {0}'.format(module_name))
            try:
                module = importlib.import_module(module_name)
                reload(module)
                return module
            except ImportError:
                lg.logger_.debug("[PREEV_MANAGER] Preevaluation function doesn't exists. " +
                                 "Aborting program...")
                sys.exit(-1)
        return None


