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

#from MLC.arduino.connection import MockConnection
import sys
sys.path.append("../..")
from MLC.arduino.connection import SerialConnection
from MLC.arduino.protocol import ArduinoInterface, REPORT_MODES
from MLC.arduino import boards
import time

def actuate(terminal):
    connection = SerialConnection(port=terminal)
    arduinoDue = ArduinoInterface(connection, boards.Due)

    arduinoDue.reset()
    arduinoDue.set_report_mode(REPORT_MODES.BULK, read_count=5, read_delay=100)    
    arduinoDue.add_output(40)
    arduinoDue.add_input(64)
    arduinoDue.add_input(63)
    arduinoDue.add_input(30)

    output = arduinoDue.actuate([(40,1)])
    for i in output.keys():
        print i
        print output[i]
        #print "Pin %d input: %s" % (output[i][0])


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "Usage: test_connection.py /dev/ttyACMX (X == number)"
        exit(-1)
    actuate(sys.argv[1:][0])

