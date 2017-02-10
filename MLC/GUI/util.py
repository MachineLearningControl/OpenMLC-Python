from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
from MLC.Common.LispTreeExpr.LispTreeExpr import ExprException
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