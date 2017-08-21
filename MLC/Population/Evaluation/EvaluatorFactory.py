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

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import MLC.Log.log as lg
import importlib
import imp
import os
import sys

from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Population.Evaluation.StandaloneEvaluator import StandaloneEvaluator


class EvaluatorFactory(object):

    @staticmethod
    def get_callback():
        function_name = Config.get_instance().get('EVALUATOR', 'evaluation_function')
        module_name = 'Evaluation.{0}'.format(function_name)

        try:
            # WARNING: I am unloading manually the evaluation function module. I need to do this
            # because Python does not support module unloading and my evaluation functions are
            # all the same, so when one experiment loads his module, other project with the same
            # name of module won't be able to load yours
            ev_module = sys.modules["Evaluation"]
            print(ev_module)
            del sys.modules['Evaluation']
            del ev_module
            lg.logger_.debug("[EV_FACTORY] Module {0} was removed".format(sys.modules["Evaluation"]))
        except KeyError as err:
            # If the module cannot be unload because it does not exists, continue
            pass

        lg.logger_.debug('[EV_FACTORY] Importing module {0}'.format(module_name))
        try:
            return imp.load_source("Evaluation." + function_name,
                                   os.path.join(*[sys.path[-1],
                                                  "Evaluation",
                                                  function_name + ".py"]))
        except ImportError as err:
            lg.logger_.debug("[EV_FACTORY] Evaluation function doesn't exists. "
                             "Aborting program. Error Msg: {0}".format(err))
            sys.exit(-1)

    @staticmethod
    def make(strategy, callback_manager):
        if strategy == "mfile_standalone":
            ev_callback = EvaluatorFactory.get_callback()
            return StandaloneEvaluator(ev_callback, callback_manager)
        else:
            lg.logger_.error("[EV_FACTORY] Evaluation method " +
                             strategy + " is not valid. Aborting program")
            sys.exit(-1)
