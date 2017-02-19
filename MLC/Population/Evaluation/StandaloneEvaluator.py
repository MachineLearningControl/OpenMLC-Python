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

import sys
import MLC.Log.log as lg

from MLC.mlc_parameters.mlc_parameters import Config
from MLC.db.mlc_repository import MLCRepository


class StandaloneEvaluator(object):

    def __init__(self, callback, callback_manager):
        self._config = Config.get_instance()
        self._callback = callback
        self._callback_manager = callback_manager

    def evaluate(self, indivs):
        jj = []

        lg.logger_.info("Evaluating %s individuals" % len(indivs))

        for index in indivs:
            lg.logger_.debug('[POP][STAND_EVAL] Individual N#' + str(index))

            # Retrieve the individual to be evaluated
            py_indiv = MLCRepository.get_instance().get_individual(index)
            lg.logger_.debug('[POP][STAND_EVAL] Individual N#' + str(index) +
                             ' Value: ' + py_indiv.get_value())

            try:
                cost = self._callback.cost(py_indiv)
                jj.append(cost)

                from MLC.Application import MLC_CALLBACKS
                self._callback_manager.on_event(MLC_CALLBACKS.ON_EVALUATE, index, cost)

            except KeyError:
                lg.logger_.error("[POP][STAND_EVAL] Evaluation Function " +
                                 "doesn't exists. Aborting progam.")
                sys.exit(-1)

        return jj
