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

import matplotlib.pyplot as plt
import sys
import time
sys.path.append("../..")

from MLC.arduino.connection import SerialConnection
from MLC.arduino.protocol import ArduinoInterface
from MLC.arduino import boards

def actuate(terminal):
    connection = SerialConnection(port=terminal)
    arduinoDue = ArduinoInterface(connection, boards.Due)

    arduinoDue.set_precision(12)
    arduinoDue.add_input(54)
    arduinoDue.add_output(40)

    last_time = time.time()
    start_time = last_time
    read_c = 0

    diff = last_time - start_time
    measures = []
    while diff < 10:
        print "Reading... {0}".format(diff)
        results = arduinoDue.actuate([(40,1)])
        measures.append(results)
        last_time = time.time()
        diff = last_time - start_time

    # Process samples
    samples = []
    for element in measures:
        for i in xrange(len(element)):
            samples.append(int(element[i][1]))

    # print "{0}".format(samples)
    print "Samples len: {0}".format(len(samples))

    plt.clf()
    plt.plot(samples)
    plt.show(block=True)

def main():
    actuate("/dev/ttyACM0")

if __name__ == "__main__":
    main()
