import MLC.Log.log as lg
import numpy as np

from MLC.individual.Individual import Individual
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.matlab_engine import MatlabEngine


def simulink_preev(indiv):
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

    # Generate the formal individual
    eng.workspace['formal'] = indiv.get_formal().replace('S0', 'signal_to_cancel')

    # Generate the input signal to be evaluated
    x = np.arange(0, amount_periods, resolution).to_list()
    pulsation = 2 * pi * signal_frequency
    signal_to_cancel = offset + signal_amplitude * np.sin(pulsation * x)

    # Pass the variables to MATLAB
    eng.workspace['signal_to_cancel'] = signal_to_cancel.to_list()
    eng.workspace['control'] = eng.eval('signal_to_cancel * 0')

    # Evaluate the individual
    eng.eval('control = control + ')


    T = [0:dT:Tev]
    signal_to_cancel = offset + A * sin(2 * pi * f * T)
    control = signal_to_cancel * 0
    idv_formal = strrep(idv_formal, 'S0', 'signal_to_cancel')
    eval(sprintf('control=control+%s;', idv_formal))

    n = length(T)
    if length(find(control <= 0)) > 0.9 * n
        fprintf('REJECT!\n')
        pre_ev_is_a_success = 0
    end

    if length(find(control > 3.3)) > 0.9 * n
        fprintf('REJECT!\n')
        pre_ev_is_a_success = 0
    end
