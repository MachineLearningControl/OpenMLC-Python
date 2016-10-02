import numpy as np
import MLC.Log.log as lg
import matplotlib.pyplot as plt
import sys
import time

from MLC.matlab_engine import MatlabEngine
from MLC.mlc_parameters.mlc_parameters import Config
from scipy import integrate

g_simulink_opened = False


def retrieve_problem_variables(config):
    values_dict = {}

    values_dict['signal_frequency'] = config.getfloat('PROBLEM_VARIABLES', 'signal_frequency')
    values_dict['signal_offset'] = config.getfloat('PROBLEM_VARIABLES', 'signal_offset')
    values_dict['resolution'] = config.getfloat('PROBLEM_VARIABLES', 'sampling_resolution')

    # To get the equivalent in time of this variable, we must divide it with
    # the signal frequency
    amount_periods = config.getfloat('PROBLEM_VARIABLES', 'amount_periods')
    # amount_periods /= values_dict['signal_frequency']
    values_dict['amount_periods'] = amount_periods
    values_dict['signal_amplitude'] = config.getfloat('PROBLEM_VARIABLES', 'signal_amplitude')

    # More parameters (This are particularly used for the Evaluation)
    values_dict['model_name'] = config.get('PROBLEM_VARIABLES', 'model_name')
    values_dict['model_path'] = config.get('PROBLEM_VARIABLES', 'model_path')
    values_dict['gamma'] = config.getfloat('PROBLEM_VARIABLES', 'gamma')
    values_dict['sensor_source'] = config.get('PROBLEM_VARIABLES', 'sensor_source')
    values_dict['goal'] = config.get('PROBLEM_VARIABLES', 'goal')
    values_dict['summator_gain'] = config.getint('PROBLEM_VARIABLES', 'summator_gain')

    return values_dict


def cost(indiv):
    global g_simulink_opened
    # Measure the time spent in the evaluation of the individual
    start_time = time.time()

    eng = MatlabEngine.engine()
    config = Config.get_instance()

    # Get problem variables
    prob_var = retrieve_problem_variables(config)
    badvalue = config.getfloat('EVALUATOR', 'badvalue')

    # Get the Individual as a formal expressions and make some replacements
    formal = indiv.get_formal()
    # Simulink does not support .*
    formal = formal.replace('.*', '*')
    # Replace the sensor with a Heaviside step function
    formal = formal.replace('S0', 'u(1)')

    model_name = prob_var['model_name']
    if not g_simulink_opened:
        # FIXME: Not exactly the best solution. It does not allow us to use
        # an already opened Simulink in other experiment
        lg.logger_.debug('[SIMULINK_EV] Starting experiment. Proceed to open Simulink')
        eng.addpath(prob_var['model_path'])
        eng.open(model_name)
        g_simulink_opened = True

    # Set Simulation parameters
    eng.set_param(model_name + '/Arduino/Control_Function', 'expression', formal, nargout=0)
    eng.set_param(model_name, 'StopTime', str(prob_var['amount_periods']), nargout=0)
    eng.set_param(model_name, 'FixedStep', str(prob_var['resolution']), nargout=0)
    eng.set_param(model_name + '/Signal_to_cancel', 'SampleTime', str(prob_var['resolution']), nargout=0)
    eng.set_param(model_name + '/Signal_to_cancel', 'Bias', str(prob_var['signal_offset']), nargout=0)
    eng.set_param(model_name + '/Signal_to_cancel', 'frequency', str(2 * np.pi * prob_var['signal_frequency']), nargout=0)
    eng.set_param(model_name + '/Ampli-op_sum/Gain', 'Gain', str(prob_var['summator_gain']), nargout=0)

    sensor_select = None
    if prob_var['sensor_source'] == 'difference':
        sensor_select = '1'
    elif prob_var['sensor_source'] == 'signal_to_cancel':
        sensor_select = '0'

    eng.set_param(model_name + '/sensor_selec', 'value', sensor_select, nargout=0)

    # Run Simulink
    eng.sim(model_name)

    # This variable has the time when the measure of the others values was taken
    # The [;,0] notation retrieves a column of a matrix. The np.array returns a (x,1) shape matrix.
    # We are converting that matrix to an array with the [:,0] notation
    clock = np.array([s for s in eng.eval('data(:,1)')])[:, 0]
    signal_to_cancel = np.array([s for s in eng.eval('data(:,2)')])[:, 0]
    sensor = np.array([s for s in eng.eval('data(:,3)')])[:, 0]
    control = np.array([s for s in eng.eval('data(:,4)')])[:, 0]
    j0 = None

    # To deal with Simulink clean crashes (???)
    if clock[-1] == prob_var['amount_periods']:
        dj_sensor = None
        dj_nat = None
        if prob_var['goal'] == 'kill_perturbation':
            dj_sensor = (sensor - np.mean(sensor))**2
            dj_nat = (signal_to_cancel - np.mean(signal_to_cancel))**2
        elif prob_var['goal'] == 'kill_signal':
            dj_sensor = sensor**2
            dj_nat = signal_to_cancel**2

        dj_control = prob_var['gamma'] * control**2
        # Cumtrapz differs with MATLAB in the way the arguments are delivered to the function
        # MATLAB: cumtrapz(x, y)
        # Scipy: np.trapz(y, x)
        j_nat = 1 / clock[-1] * integrate.cumtrapz(dj_nat, clock)

        # Use Jnat to normalize the vectors
        j_sensor = 1 / clock[-1] * integrate.cumtrapz(dj_sensor, clock) / j_nat[-1]
        j_control = 1 / clock[-1] * integrate.cumtrapz(dj_control, clock) / j_nat[-1]
        j0 = j_sensor[-1] + j_control[-1]

        lg.logger_.debug("Jnat: {0} - Jsensor: {1} - Jcontrol: {2} - J0: {3}"
                         .format(j_nat[-1], j_sensor[-1], j_control[-1], j0))

        # Evaluate the result of the j calculated
        zero_condition = np.sum(j_control < 0.0)
        if zero_condition > len(clock) * 0.9:
            j0 = badvalue

        offset_condition = np.sum(j_control > prob_var['signal_offset'])
        if offset_condition > len(clock) * 0.9:
            j0 = badvalue

        if j0 > badvalue:
            lg.logger_.info('[SIMULINK_EV] Cost exceeded maximum value.')
        else:
            lg.logger_.info('[SIMULINK_EV] Evaluation succesful. Cost: {0}'.format(j0))

        elapsed_time = time.time() - start_time
        lg.logger_.debug('[SIMULINK_EV] Evaluation elapsed time: {0}'.format(elapsed_time))
    else:
        j0 = badvalue

    return j0
