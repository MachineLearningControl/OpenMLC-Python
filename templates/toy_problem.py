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

# -*- coding: utf-8 -*-

import numpy as np
import MLC.Log.log as lg
import matplotlib.pyplot as plt
import random
import sys
import time

from MLC.arduino.protocol import ArduinoUserInterface
from MLC.mlc_parameters.mlc_parameters import Config
from PyQt5.QtCore import Qt


def individual_data(indiv):
    SAMPLES = 201
    x = np.linspace(-10.0, 10.0, num=SAMPLES)
    y = np.tanh(x**3 - x**2 - 1)

    config = Config.get_instance()
    artificial_noise = config.getint('EVALUATOR', 'artificialnoise')
    y_with_noise = y + [random.random() / 2 - 0.25 for _ in xrange(SAMPLES)] + artificial_noise * 500

    if isinstance(indiv.get_formal(), str):
        formal = indiv.get_formal().replace('S0', 'x')
    else:
        # toy problem support for multiple controls
        formal = indiv.get_formal()[0].replace('S0', 'x')

    # Calculate J like the sum of the square difference of the
    # functions in every point
    lg.logger_.debug('[POP][TOY_PROBLEM] Individual Formal: ' + formal)
    b = indiv.get_tree().calculate_expression([x])

    # If the expression doesn't have the term 'x',
    # the eval returns a value (float) instead of an array.
    # In that case transform it to an array
    if type(b) == float:
        b = np.repeat(b, SAMPLES)

    return x, y, y_with_noise, b


def cost(indiv):
    x, y, y_with_noise, b = individual_data(indiv)

    # Deactivate the numpy warnings, because this sum could raise an overflow
    # Runtime warning from time to time
    np.seterr(all='ignore')
    cost_value = float(np.sum((b - y_with_noise)**2))
    np.seterr(all='warn')

    return cost_value


def show_best(index, generation, indiv, cost, block=True):
    x, y, y_with_noise, b = individual_data(indiv)
    mean_squared_error = np.sqrt((y_with_noise - b)**2 / (1 + np.absolute(x**2)))

    # Put figure window on top of all other windows
    fig = plt.figure()
    fig.canvas.manager.window.setWindowModality(Qt.ApplicationModal)
    fig.canvas.manager.window.setWindowTitle("Best Individual")

    formal = None
    if type(indiv.get_formal()) == list:
        formal = indiv.get_formal()[0]
    else:
        formal = indiv.get_formal()

    plt.rc('font', family='serif')
    plt.suptitle("Generation N#{0} - Individual N#{1}\n"
                 "Cost: {2}\n Formal: {3}".format(generation,
                                                  index,
                                                  cost,
                                                  formal),
                 fontsize=12)

    plt.subplot(2, 1, 1)
    line1, = plt.plot(x, y, color='r', linewidth=4, label='Curve without noise')
    line2, = plt.plot(x, y_with_noise, 'g-.', linewidth=2, label='Curve with noise')
    line3, = plt.plot(x, b, color='k', linewidth=2, label='Control Law (Individual)')
    plt.ylabel('Functions', fontsize=12, fontweight='bold')
    plt.xlabel('Samples', fontsize=12, fontweight='bold')
    plt.legend(handles=[line1, line2, line3], loc=2)
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(x, mean_squared_error, '*r')
    plt.ylabel('Mean Squared Error', fontsize=12, fontweight='bold')
    plt.xlabel('Samples', fontsize=12, fontweight='bold')
    plt.grid(True)
    plt.yscale('log')

    plt.show(block=block)
