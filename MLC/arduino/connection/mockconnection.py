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

from MLC.arduino.connection.base import BaseConnection


class MockConnection(BaseConnection):
    """ Connection that save the data sent using "send" method and response 
        on a "recv" call using a pre-configured response buffer
    """

    def __init__(self, responses):
        """ response -- bytes stream of responses that will be used in recv method """
        self._received = []
        self._responses = responses
        self._resp_idx = 0

    def send(self, data):
        """ \"sends\" the data to a inner buffer """
        self._received.insert(0, data)

    def pop_data(self):
        """ Pops a complete data stream received """
        return self._received.pop()

    def recv(self, length):
        """
        Looping receiver (if buffer run out of data, it add to the response bytes from the beginning)

        length -- count of bytes to \"receive\"
        """
        pos = self._resp_idx
        if pos + length > len(self._responses):
            self._resp_idx = (length - (len(self._responses) - pos)) % len(self._responses)
            return self._responses[pos:] + self._responses[0:length - (len(self._responses) - pos)]

        self._resp_idx = pos + length
        return self._responses[pos:pos + length]
