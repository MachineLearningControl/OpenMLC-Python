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


class ConnectionException(Exception):
    pass


class ConnectionTimeoutException(ConnectionException):
    def __init__(self, what):
        ConnectionException.__init__(self, "Connection timeout: %s" % (what))


class BaseConnection:
    '''
    Connection base class
    
    Defines method for I/O with an Arduino device
    '''
    def send(self, data):
        """ Sends data to arduino device """
        raise NotImplementedError

    def recv(self, length):
        """ Receive data from the arduino device """
        raise NotImplementedError

    def wake_up(self):
        raise NotImplementedError


class InvalidConnection(BaseConnection):
    def __init__(self):
        return

    def send(self, data):
        raise ConnectionException("Invalid setup of connection")

    def recv(self, length):
        raise ConnectionException("Invalid setup of connection")

    def wake_up(self):
        raise ConnectionException("Invalid setup of connection")


def invalid_connection_builder(params):
    return InvalidConnection()