#! /usr/bin/python2.7
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

import serial
import time
from struct import *

def main():
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=2.0)
    time.sleep(1)
    print "PRENDIENDO ALARMA DE QUE ESTA TODO BIEN!!"

    port1 = 10
    port2 = 8
    # Start configuration 
    send_command(ser, pack('BB', 1, 2))

    # Set port 10 as output
    send_command(ser, pack('BB', 10, 6))
    send_command(ser, pack('BBBB', port1, 2, port2, 2)) 

    # End configuration
    send_command(ser, pack('BB', 2, 2))

    # Turn on port 8 and 4
    send_command(ser, pack('BB', 20, 4))
    send_command(ser, pack('BB', port1, 1))
    time.sleep(5)

    # Toggle ports
    send_command(ser, pack('BB', 20, 6))
    send_command(ser, pack('BBBB', port1, 0, port2, 1))
    time.sleep(5)

    # Turn both
    send_command(ser, pack('BB', 20, 6))
    send_command(ser, pack('BBBB', port1, 1, port2, 1))
    time.sleep(5)

    # Turn off both leds
    send_command(ser, pack('BB', 20, 6))
    send_command(ser, pack('BBBB', port1, 0, port2, 0))

def send_command(ser, cmd):
    ser.write(cmd)
    while ser.inWaiting() < 4:
        continue

    bytesToRead = ser.inWaiting()
    bytesRead = ser.read(bytesToRead)
    response = unpack("B" * bytesToRead, bytesRead)

    if response is not None:
        print response

    if response[0] != 3:
        raise RuntimeError

if __name__ == "__main__":
    main()


