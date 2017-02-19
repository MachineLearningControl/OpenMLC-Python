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
from MLC.arduino.connection import SerialConnection
import MLC.arduino.protocol as protocol
from MLC.arduino.protocol import ArduinoInterface
from MLC.arduino import boards
import MLC.arduino 
import sys
import time


BREAK_COUNT=20000

def actuate(terminal):
    global BREAK_COUNT
    connection = SerialConnection(port=terminal)
    arduinoDue = ArduinoInterface(connection, boards.Due)
    
    arduinoDue.reset() #Just in case
    arduinoDue.set_report_mode(protocol.REPORT_MODES.AVERAGE, read_count=50, read_delay=0)
    
    arduinoDue.add_output(40)
    arduinoDue.add_output(66)
#    arduinoDue.add_input(65)
#    arduinoDue.add_input(64)
#    arduinoDue.add_input(63)
#    arduinoDue.add_input(62)
#    arduinoDue.add_input(61)
#    arduinoDue.add_input(60)
#    arduinoDue.add_input(59)
#    arduinoDue.add_input(58)
#    arduinoDue.add_input(57)
#    arduinoDue.add_input(56)
#    arduinoDue.add_input(55)
    arduinoDue.add_input(54)
    arduinoDue.add_input(55)

    last_time = time.time()
    start_time = last_time
    read_c = 0
    
    for i in xrange(0, BREAK_COUNT):
        output = arduinoDue.actuate([(40,1),(66,255)])
        #print output
        read_c = read_c + 1
        new_time = time.time()

        if (new_time - start_time) > 1:
           print str(read_c-1) # The current read was out of the period
           read_c = 1
           start_time = new_time

        last_time = new_time


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "Usage: test_connection.py /dev/ttyACMX (X == number)"
        exit(-1)
    actuate(sys.argv[1:][0])

