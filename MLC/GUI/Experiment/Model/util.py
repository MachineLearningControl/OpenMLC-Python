from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
from MLC.Common.LispTreeExpr.LispTreeExpr import ExprException
from MLC.individual.Individual import Individual
from MLC.Log.log import get_gui_logger
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory

logger = get_gui_logger()


def test_individual_value(experiment_name, log_prefix, indiv_value, config):
    err_string = None
    try:
        """
        Evaluate an individual in order to check its correctness. Handle Exceptions
        """
        LispTreeExpr.check_expression(indiv_value)
        individual = Individual.generate(config=config,
                                         rhs_value=indiv_value)
        callback = EvaluatorFactory.get_callback()
        return callback.cost(individual), err_string
    except ExprException, err:
        # Print the error message returned in the exception,
        # removing the prefix ([EXPR_EXCEPTION]])
        err_string = ("{0} Experiment {1} - "
                      "Individual inserted is not well-formed. "
                      "Error Msg: {2}"
                      .format(log_prefix, experiment_name,
                              err.message[err.message.find(']') + 2:]))
        logger.error(err_string)
    except Exception, err:
        err_string = ("{0} Experiment {1} - "
                      "Individual inserted is not a valid individual. "
                      "Check the evaluation script to be correct. "
                      "Error Msg: {2}."
                      .format(log_prefix, experiment_name, err))
        logger.error(err_string)

    return None, err_string


def check_individual_value(experiment_name, log_prefix, indiv_value):
    view_error_string = None
    try:
        """
        Evaluate an individual in order to check its correctness. Handle Exceptions
        """
        LispTreeExpr.check_expression(indiv_value)
        return True, None
    except ExprException, err:
        # Print the error message returned in the exception,
        # removing the prefix ([EXPR_EXCEPTION]])
        err_string = ("{0} Experiment {1} - "
                      "Individual inserted is not well-formed. "
                      "Error Msg: {2}"
                      .format(log_prefix, experiment_name,
                              err.message[err.message.find(']') + 2:]))
        logger.error(err_string)

        view_error_string = ("Individual inserted is not well-formed. Error Msg: {0}"
                             .format(err.message[err.message.find(']') + 2:]))
    return False, view_error_string
