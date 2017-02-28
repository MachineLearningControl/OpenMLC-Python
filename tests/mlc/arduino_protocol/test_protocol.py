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

import unittest
from MLC.arduino.connection import MockConnection
from MLC.arduino.protocol import ArduinoInterface, ProtocolSetupException, ProtocolIOException
from MLC.arduino.protocol import REPORT_MODES
from MLC.arduino import boards

ACK = "\xFF\x00\x00\x00\x00"
NACK = "\xFF\x00\x00\x00\x01"
REPORT = "\xF1\x00\x00\x00\x05\x10\x01\x3D\x05\x20"
REPORT_B = "\xF1\x00\x00\x00\x1A\x10\xF1\x0A\x3D\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00"
REPORT_C = "\xF1\x00\x00\x00\x16\x3D\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x3E\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00"


class TestArduinoInterface(unittest.TestCase):
    def setUp(self):
        self._connection = MockConnection(ACK)
        self._interface = ArduinoInterface(self._connection, boards.Due)

    def test_set_precision(self):
        self._interface.set_precision(12)
        data = self._connection.pop_data()
        self.assertEqual("\x01\x00\x00\x00\x01\x0C", data)
        with self.assertRaises(ValueError):
            self._interface.set_precision(33)

    def test_report_mode(self):
        self._interface.set_report_mode(REPORT_MODES.AVERAGE)
        data = self._connection.pop_data()
        self.assertEqual("\x05\x00\x00\x00\x03\x00\x00\x00", data)
        self._interface.set_report_mode(REPORT_MODES.AVERAGE, read_count=10, read_delay=5)
        data = self._connection.pop_data()
        self.assertEqual("\x05\x00\x00\x00\x03\x00\x09\x05", data)
        with self.assertRaises(ValueError):
            self._interface.set_report_mode(12334)  # Invalid report mode

    def test_add_input(self):
        self._interface.add_input(60)
        data = self._connection.pop_data()
        self.assertEqual("\x02\x00\x00\x00\x01\x3C", data)
        data = self._connection.pop_data()
        self.assertEqual("\x04\x00\x00\x00\x02\x3C\x00", data)
        self._interface.add_input(60)
        with self.assertRaises(Exception):  # Checks that no data has been sent
            data = self._connection.pop_data()
        with self.assertRaises(ValueError):  # Checks that no data has been sent
            self._interface.add_output(128)

    def test_add_output(self):
        self._interface.add_output(60)
        data = self._connection.pop_data()
        self.assertEqual("\x03\x00\x00\x00\x01\x3C", data)
        data = self._connection.pop_data()
        self.assertEqual("\x04\x00\x00\x00\x02\x3C\x01", data)
        self._interface.add_output(60)
        with self.assertRaises(Exception):  # Checks that no data has been sent
            data = self._connection.pop_data()
        with self.assertRaises(ValueError):  # Checks that no data has been sent
            self._interface.add_output(128)

    def test_error_adding_output_that_is_input(self):
        self._interface.add_input(60)
        with self.assertRaises(ProtocolSetupException):
            self._interface.add_output(60)

    def test_actuate_error_response(self):
        self._interface.add_output(60)
        self._connection.pop_data()
        with self.assertRaises(ProtocolIOException):
            self._interface.actuate([(60, 128)])

    def test_actuate_with_one_read(self):
        self._connection = MockConnection(REPORT)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.add_output(60)
        self._interface.add_input(16)
        self._interface.add_input(61)
        response = self._interface.actuate([(60, 128)])
        self.assertEqual(1, len(response["D16"]))
        self.assertTrue(response["D16"][0])
        self.assertEqual(1, len(response["A7"]))
        self.assertEqual(0x0520, response["A7"][0])

    def test_actuate_with_many_readings(self):
        self._connection = MockConnection(REPORT_B)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.set_report_mode(REPORT_MODES.BULK, read_count=11, read_delay=5)
        self._interface.add_output(60)
        self._interface.add_input(61)
        self._interface.add_input(16)
        response = self._interface.actuate([(60, 128)])
        self.assertEqual(2, len(response))
        self.assertTrue("D16" in response.keys())
        self.assertEqual(11, len(response["D16"]))
        self.assertTrue(response["D16"][0])
        self.assertTrue(response["D16"][6])
        self.assertTrue(response["D16"][7])
        self.assertFalse(response["D16"][8])
        self.assertTrue(response["D16"][9])
        self.assertFalse(response["D16"][10])
        for i in range(0, 11):
            self.assertEqual(0x0100, response["A7"][i])

    def test_actuate_with_many_pins_readings(self):
        self._connection = MockConnection(REPORT_C)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.set_report_mode(REPORT_MODES.BULK, read_count=5, read_delay=5)
        self._interface.add_output(60)  # Pin A6
        self._interface.add_input(61)   # Pin A7
        self._interface.add_input(62)   # Pin A8
        response = self._interface.actuate([(60, 128)])
        for i in range(0, 5):
            self.assertEqual(0x0100, response["A7"][i])
        for i in range(0, 5):
            self.assertEqual(0x0100, response["A8"][i])

    def test_average(self):
        self._connection = MockConnection(REPORT_B)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.set_report_mode(REPORT_MODES.AVERAGE, read_count=11, read_delay=5)
        self._interface.add_output(boards.Due["ANALOG_PINS"][6])
        self._interface.add_input(boards.Due["ANALOG_PINS"][7])   # Pin A7
        self._interface.add_input(boards.Due["DIGITAL_PINS"][16])
        response = self._interface.actuate([(60, 128)])
        self.assertEqual(2, len(response))
        self.assertEqual(1, len(response["D16"]))
        self.assertTrue(response["D16"][0])
        self.assertEqual(0x0100, response["A7"][0])
