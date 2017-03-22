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

import numpy as np
import MLC.Log.log as lg
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import time

from matplotlib import rc
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


def individual_data(indiv):
    """
    Returns as a dict: * clock
                       * dj_nat
                       * j_nat
                       * dj_sensor
                       * j_sensor
                       * dj_control
                       * j_control
    """
    global g_simulink_opened
    # Measure the time spent in the evaluation of the individual
    start_time = time.time()

    eng = MatlabEngine.engine()
    config = Config.get_instance()

    # Get problem variables
    prob_var = retrieve_problem_variables(config)
    badvalue = config.getfloat('EVALUATOR', 'badvalue')

    # Get the Individual as a formal expressions and make some replacements
    formal = None
    if type(indiv.get_formal()) == list:
        formal = indiv.get_formal()[0]
    else:
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
        zero_condition = np.sum(j_control <= 0.0)
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

    simulink_results = {}
    simulink_results["clock"] = clock
    simulink_results["signal_to_cancel"] = signal_to_cancel
    simulink_results["sensor"] = sensor
    simulink_results["control"] = control
    simulink_results["dj_nat"] = dj_nat
    simulink_results["j_nat"] = j_nat
    simulink_results["dj_sensor"] = dj_sensor
    simulink_results["j_sensor"] = j_sensor
    simulink_results["dj_control"] = dj_control
    simulink_results["j_control"] = j_control
    simulink_results["j0"] = j0
    return simulink_results


def cost(indiv):
    simulink_results = individual_data(indiv)
    return simulink_results['j0']


def show_best(index, generation, indiv, cost, block=True):
    # TODO: Add texlive-latex-extra and textlive-latex-recommended in the Wiki if we want to use LaTeX fonts
    sl_results = individual_data(indiv)
    config = Config.get_instance()
    problem_variables = retrieve_problem_variables(config)
    fig_title = create_figure_title(problem_variables, indiv.get_value())

    fig = plt.figure()
    # Put figure window on top of all other windows
    fig.canvas.manager.window.setWindowModality(Qt.ApplicationModal)

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.suptitle(fig_title)

    plt.subplot(3, 1, 1)
    line1, = plt.plot(sl_results["clock"], sl_results["signal_to_cancel"], linewidth=1.2, linestyle='-', color='g', label='signal')
    line2, = plt.plot(sl_results["clock"], sl_results["sensor"], linewidth=1.2, linestyle='-', color='b', label='ampli')
    line3, = plt.plot(sl_results["clock"], sl_results["control"], linewidth=1.2, linestyle='-', color='r', label='control')
    plt.xlabel('T(s)', fontsize=12)
    plt.ylabel('Voltages (V)', fontsize=16)
    plt.legend(handles=[line1, line2, line3], loc=1)
    plt.grid(True)

    plt.subplot(3, 1, 2)
    signal_part1 = (sl_results["sensor"] - np.mean(sl_results["sensor"]))**2
    signal_part2 = problem_variables["gamma"] * np.abs(sl_results["control"])**2
    line1, = plt.plot(sl_results["clock"], signal_part1 + signal_part2, linewidth=2, linestyle='-', color='k', label='dJ Total')
    line2, = plt.plot(sl_results["clock"], signal_part1, linewidth=1.2, linestyle='-', color='b', label='dJ sensor')
    line3, = plt.plot(sl_results["clock"], signal_part2, linewidth=1.2, linestyle='-', color='r', label='dJ control')
    plt.xlabel('T(s)', fontsize=12)
    plt.ylabel('dJ', fontsize=16)
    plt.legend(handles=[line1, line2, line3], loc=1)
    plt.grid(True)

    plt.subplot(3, 1, 3)
    line1, = plt.plot(sl_results['j_sensor'] + sl_results['j_control'], linewidth=1.2, linestyle='-', color='k', label='total')
    line2, = plt.plot(sl_results['j_sensor'], linewidth=1.2, linestyle='-', color='b', label='sensor')
    line3, = plt.plot(sl_results['j_control'], linewidth=1.2, linestyle='-', color='r', label='control')
    plt.xlabel('T(s)', fontsize=12)
    plt.ylabel('$\int_0^t dJ \mathrm{d}t/J_{nat}$', fontsize=16);
    plt.legend(handles=[line1, line2, line3], loc=1)
    plt.grid(True)

    plt.show(block=block)


def create_figure_title(problem_variables, indiv_value):
    tit_sum = None
    if problem_variables['summator_gain'] == -1:
        tit_sum = 'difference'
    else:
        tit_sum = 'summation'

    tit_sensor = None
    if problem_variables['sensor_source'] == 'difference':
        tit_sensor = 'ampli-op output (blue curve)'
    else:
        tit_sensor = 'initial signal (green curve)'

    tit_goal = None
    if problem_variables['goal'] == 'kill_signal':
        tit_goal = 'signal (RMS)'
    else:
        tit_goal = 'perturbation (STD)'

    title = ('Ampli-op mode: {0} \n Sensor Choice: {1} \n Goal To Achieve: {2} supression \n This Law: {3}'
             .format(tit_sum, tit_sensor, tit_goal, indiv_value))
    return title
