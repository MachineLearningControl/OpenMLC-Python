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

from base import BaseConnection
from collections import namedtuple
import serial


class SerialConnection(BaseConnection):

    def __init__(self, **args):
        """ Starts a serial connection

        Keyword arguments:
        port -- connection to the device. In Linux: /dev/ttyXXX On Windows: COMX. This options is mandatory!
        baudrates -- baurates of the connection. By default will be set to 115200
        parity -- parity check bits from pySerial. By default it is set to PARITY_ONE. Available options: PARITY_EVEN, PARITY_ODD, PARITY_MARK & PARITY_SPACE
        stopbits -- stop bits from pySerial. By default it is set to STOPBITS_ONE. Available options: STOPBITS_ONE_POINT_FIVE & STOPBITS_TWO
        bytesize -- byte size from pySerial. By default it is set to EIGHTBITS. Available options: FIVEBITS, SIXBITS & SEVENBITS
        """
        if "port" not in args.keys():
            raise Exception("Port is mandatory!")

        args["baudrate"] = 115200 if "baudrate" not in args.keys() else args["baudrate"]
        args["parity"] = serial.PARITY_NONE if "parity" not in args.keys() else args["parity"]
        args["stopbits"] = serial.STOPBITS_ONE if "stopbits" not in args.keys() else args["stopbits"]
        args["bytesize"] = serial.EIGHTBITS if "bytesize" not in args.keys() else args["bytesize"]
        args["timeout"] = 5
        args["write_timeout"] = 5

        self._connection = serial.Serial(**args)

    def send(self, data):
        self._connection.write(data)

    def recv(self, length):
        """ Receives the specified amount of bytes
        WARNING: This function is blocked until receive the amount of bytes

        Keyword arguments:
        length -- amount of bytes to receive
        """
        recv = self._connection.read(length)

        if len(recv) != length:
            raise serial.SerialTimeoutException
        else:
            return recv


class SerialConnectionConfig (namedtuple('SerialConnectionConfig', ['port', 'baudrate', 'parity', 'stopbits', 'bytesize'])):

    def __new__(cls, port, baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS):
        return super(SerialConnectionConfig, cls).__new__(cls, port, baudrate, parity, stopbits, bytesize)
