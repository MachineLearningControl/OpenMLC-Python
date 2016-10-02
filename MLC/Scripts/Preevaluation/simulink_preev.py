import MLC.Log.log as lg
import numpy as np

from MLC.individual.Individual import Individual
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.matlab_engine import MatlabEngine


def preev(indiv):
    eng = MatlabEngine.engine()
    config = Config.get_instance()

    # Get problem variables
    signal_frequency = config.getfloat('PROBLEM_VARIABLES', 'signal_frequency')
    signal_offset = config.getfloat('PROBLEM_VARIABLES', 'signal_offset')
    resolution = config.getfloat('PROBLEM_VARIABLES', 'sampling_resolution')

    # To get the equivalent in time of this variable, we must divide it with
    # the signal frequency
    amount_periods = config.getfloat('PROBLEM_VARIABLES', 'amount_periods')
    amount_periods /= signal_frequency
    signal_amplitude = config.getfloat('PROBLEM_VARIABLES', 'signal_amplitude')

    # Generate the input signal to be evaluated
    x = np.arange(0, amount_periods, resolution)
    pulsation = 2 * np.pi * signal_frequency
    signal_to_cancel = signal_offset + signal_amplitude * np.sin(pulsation * x)

    # Evaluate the individual formal
    indiv_evaluated = indiv.get_tree().calculate_expression([signal_to_cancel])
    if type(indiv_evaluated) != np.ndarray:
        indiv_evaluated = np.repeat(indiv_evaluated, len(x))

    # The condition to discard or not the individual will be the number of
    # elements of certain range (0 / 3.3)
    cut_condition = 0.9 * len(indiv_evaluated)
    zero_condition = np.sum(indiv_evaluated <= 0.0)
    if zero_condition > cut_condition:
        lg.logger_.debug("[SIMULINK_PREEV] Individual didn't pass "
                 "greater than zero condition. LT Zero: {0}  - Max Expected: {1}. Indiv: {2}"
                 .format(zero_condition, cut_condition, indiv.get_formal()))
        return False

    max_value = signal_offset * 2
    offset_condition = np.sum(indiv_evaluated > max_value)
    if offset_condition > cut_condition:
        lg.logger_.debug("[SIMULINK_PREEV] Individual didn't pass "
                 "less than max_value condition. GT Offset: {0}  - Max Expected: {1}. Indiv: {2}"
                 .format(offset_condition, cut_condition, indiv.get_formal()))
        return False

    lg.logger_.debug("[SIMULINK_PREEV] Individual passed: {0}".format(indiv.get_formal()))

    return True
