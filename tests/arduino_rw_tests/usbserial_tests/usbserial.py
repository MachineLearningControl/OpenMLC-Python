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

import time
import serial
import struct

RW_OPERATIONS=300000


'''
Test I/O operations using Serial connection to the arduino

Setting as port the ArduinoDUE native USB (and loading the related test script in the ArduinoDUE board)
this scripts test how many write/read operations per second are allowed but this port.

The output of the script is print on stdout. The RW_OPERATIONS var sets the the max number of R/W op.
to accomplish in order to finalize the test.
'''

ser = serial.Serial(
   port='/dev/ttyACM0',
   baudrate=115200,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS
)

WRITE_DATA="123456789012" # Data to send to the Arduino

best = 1000;
worst = 0;
read_c = 0;

last_time = time.time()
start_time = last_time
for i in range(1,RW_OPERATIONS):
    ser.write(WRITE_DATA)
    data = ser.read(4); # The data send by the Arduino must have a length byte. This is mandatory due 
                        # that serial read blocks until it has read the specified count of bytes
    n = struct.unpack("<L", data)[0]; # Gets long representation
    data = ser.read(n);
    new_time = time.time()
    get_time = new_time - last_time
    #print 'Operation delay in ' + str(get_time) + ' seconds'
    read_c = read_c + 1
    
    if new_time-last_time < best:
       best = get_time

    if new_time-last_time > worst:
       worst = get_time
    
    if (new_time - start_time) > 1:
       print str(read_c-1) # The current read was out of the period
       read_c = 1
       start_time = new_time
    
    #print 'best: ' + str(best) + ' worst: ' + str(worst)
    last_time = new_time
