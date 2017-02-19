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

import os

from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
from MLC.Common.LispTreeExpr.LispTreeExpr import ExprException
from MLC.Common.PreevaluationManager import PreevaluationManager
from MLC.individual.Individual import Individual
from MLC.Log.log import get_gui_logger
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from PyQt5.QtWidgets import QMessageBox

logger = get_gui_logger()

"""
Utilities functions used in more than one class or python module
"""


def test_individual_value(parent, experiment_name, log_prefix, indiv_value, config):
    try:
        """
        Evaluate an individual in order to check its correctness. Handle Exceptions
        """
        LispTreeExpr.check_expression(indiv_value)
        individual = Individual.generate(config=config,
                                         rhs_value=indiv_value)
        callback = EvaluatorFactory.get_callback()
        return callback.cost(individual)
    except ExprException, err:
        # Print the error message returned in the exception,
        # removing the prefix ([EXPR_EXCEPTION]])
        QMessageBox.critical(parent,
                             "Invalid Individual",
                             "Individual inserted is not well-formed. "
                             "Error Msg: {0}"
                             .format(err.message[err.message.find(']') + 2:]))
        logger.error("{0} Experiment {1} - "
                     "Individual inserted is not well-formed. "
                     "Error Msg: {2}"
                     .format(log_prefix, experiment_name,
                             err.message[err.message.find(']') + 2:]))
    except Exception, err:
        QMessageBox.critical(parent,
                             "Invalid Evaluation Script",
                             "Check the evaluation script to be correct. "
                             "Error Msg: {0}.".format(err))
        logger.error("{0} Experiment {1} - "
                     "Individual inserted is not a valid individual. "
                     "Check the evaluation script to be correct. "
                     "Error Msg: {2}."
                     .format(log_prefix, experiment_name, err))

    return None


def check_individual_value(parent, experiment_name, log_prefix, indiv_value, nodialog=False):
    try:
        """
        Evaluate an individual in order to check its correctness. Handle Exceptions
        """
        LispTreeExpr.check_expression(indiv_value)
        return True
    except ExprException, err:
        # Print the error message returned in the exception,
        # removing the prefix ([EXPR_EXCEPTION]])
        if not nodialog:
            QMessageBox.critical(parent,
                                 "Invalid Individsual",
                                 "Individual inserted is not well-formed. "
                                 "Error Msg: {0}"
                                 .format(err.message[err.message.find(']') + 2:]))
        logger.error("{0} Experiment {1} - "
                     "Individual inserted is not well-formed. "
                     "Error Msg: {2}"
                     .format(log_prefix, experiment_name,
                             err.message[err.message.find(']') + 2:]))
    return False


def check_if_indiv_pass_preevaluation(parent, experiment_name, log_prefix, indiv_value, config):
    try:
        """
        Evaluate an individual in order to check its correctness. Handle Exceptions
        """
        LispTreeExpr.check_expression(indiv_value)
        individual = Individual.generate(config=config,
                                         rhs_value=indiv_value)
        callback = PreevaluationManager.get_callback()
        return callback.preev(individual)
    except ExprException, err:
        # Print the error message returned in the exception,
        # removing the prefix ([EXPR_EXCEPTION]])
        QMessageBox.critical(parent,
                             "Invalid Individual",
                             "Individual inserted is not well-formed. "
                             "Error Msg: {0}"
                             .format(err.message[err.message.find(']') + 2:]))
        logger.error("{0} Experiment {1} - "
                     "Individual inserted is not well-formed. "
                     "Error Msg: {2}"
                     .format(log_prefix, experiment_name,
                             err.message[err.message.find(']') + 2:]))
    except Exception, err:
        QMessageBox.critical(parent,
                             "Invalid Evaluation Script",
                             "Check the evaluation script to be correct. "
                             "Error Msg: {0}.".format(err))
        logger.error("{0} Experiment {1} - "
                     "Individual inserted is not a valid individual. "
                     "Check the evaluation script to be correct. "
                     "Error Msg: {2}."
                     .format(log_prefix, experiment_name, err))

    return None


def add_permissions_to_file(filepath, permissions, user_password=None):
    # Create the command to execute
    cmd = 'chmod {0} {1}'.format(permissions, filepath)
    logger.info('Proceed to give {0} permissions to file {1}'.format(permissions, filepath))
    if user_password:
        cmd_error_code = os.system('echo %s |sudo -S %s' % (user_password, cmd))
        # Erase the passwd stored, so sudo obliged us to insert it again
        os.system('sudo -K')
        return cmd_error_code == 0
    else:
        return os.system(cmd) == 0