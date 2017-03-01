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

import collections
import boards
from collections import namedtuple
from connection.base import ConnectionException
import MLC.Log.log as lg

_PROTOCOL_CMDS = {"ANALOG_PRECISION": '\x01\x00\x00\x00\x01%s',
                  "SET_INPUT": '\x02\x00\x00\x00\x01%s',
                  "SET_OUTPUT": '\x03\x00\x00\x00\x01%s',
                  "PIN_MODE": '\x04\x00\x00\x00\x02%s%s',
                  "REPORT_MODE": '\x05\x00\x00\x00\x03%s%s%s',
                  "ANALOG_WRITE": '\x06\x00\x00\x00\x03%s%s%s',
                  "ACK": '\xFF',
                  "ACTUATE": '\xF0',
                  "PROT_VERSION": '\xF2\x00\x00\x00\x00',
                  "RESET": '\xFE\x00\x00\x00\x00',
                  "ACTUATE_REPORT": '\xF1'}

REPORT_MODES = collections.namedtuple(
    'REPORT_MODES', ['AVERAGE', 'BULK', 'RT'], verbose=False)(AVERAGE=0, BULK=1, RT=2)
PIN_MODES = collections.namedtuple(
    'PIN_MODES', ['INPUT', 'OUTPUT'], verbose=False)(INPUT=0, OUTPUT=1)

class ProtocolException(Exception):
    pass

class ProtocolIOException(ProtocolException):
    def __init__(self,what):
        ProtocolException.__init__(self, "Protocol IO error: %s" % (what))

class ProtocolSetupException(ProtocolException):
    def __init__(self, what):
        ProtocolException.__init__(self, "Setup error: %s" % (what))

class ArduinoInterfaceSingleton():
    _instance = None

    @staticmethod
    def get_instance(protocol_config=None, conn_setup=None):
        from MLC.arduino.connection.serialconnection import SerialConnection
        if protocol_config and conn_setup:

            serial_conn = None
            try:
                serial_conn = SerialConnection(**conn_setup)
            except ConnectionException, err:
                lg.logger_.info("[PROTOCOL] Error while loading SerialConnection. "
                                "Err info: {0}".format(err))
                raise

            protocol_config = protocol_config._replace(connection=serial_conn)
            ArduinoInterfaceSingleton._instance = BuildSerial(protocol_config)

        if ArduinoInterfaceSingleton._instance is None:
            raise ProtocolSetupException("The arduino interface cannot be used if it isn't configured.")

        return ArduinoInterfaceSingleton._instance


class ArduinoInterface:
    # 0=input 1=output -- wiring_constants.h

    def __init__(self, connection, board):
        self._connection = connection
        self._anlg_inputs = []
        self._digital_inputs = []
        self._anlg_outputs = []
        self._digital_outputs = []
        self._anlg_precition = 10  # Default Arduino analog precision
        self._report_mode = REPORT_MODES.AVERAGE
        self._read_count = 0  # Default number of inputs read
        self._read_delay = 0
        self._board = board

    def get_analog_inputs(self):
        return self._anlg_inputs()

    def get_digital_inputs(self):
        return self._digital_inputs

    def get_analog_precition(self):
        return self._analog_precition

    def get_report_modes(self):
        return self._report_mode

    def get_read_count(self):
        return self._read_count

    def get_board(self):
        return self._board

    def get_version(self):
        self._connection.send(_PROTOCOL_CMDS["PROT_VERSION"])
        response = self._connection.recv(1)
        length = ord(self._connection.recv(1))
        return self._connection.recv(length)

    def set_pwm(self, pin, duty_cicle):
        if port in self._anlg_inputs or port in self._digital_inputs:
            raise ProtocolSetupException("Port %s is configured as input!" % self.__get_arduino_pin(port))

        self._connection.send(_PROTOCOL_CMDS["ANALAOG_WRITE"] % (
            chr(pin), chr((duty_cicle & 0xFF00) >> 8), chr(duty_cicle & 0x00FF)))

    def set_precision(self, bits):
        if bits > 32 or bits < 1:
            raise ValueError("Precision bits must be between 1 and 32!")
        self._connection.send(_PROTOCOL_CMDS["ANALOG_PRECISION"] % chr(bits))
        self._anlg_precition = bits

    def __set_pin_mode(self, port, mode):
        if mode not in PIN_MODES._asdict().values():
            raise ValueError("Pind mode error. Unknown mode: %s. Modes availables: %s " %
                            (mode, str(PIN_MODES_asdict().keys())))

        self._connection.send(
            _PROTOCOL_CMDS["PIN_MODE"] % (chr(port), chr(mode)))

    def set_report_mode(self, mode, read_count=1, read_delay=0):
        if mode not in REPORT_MODES._asdict().values():
            raise ValueError("Report mode error. Unknown value: %s" % mode)

        if read_count <= 0:
            raise ValueError("Read count value must be > 0")

        self._report_mode = mode
        self._read_count = read_count - 1
        self._read_delay = read_delay

        self._connection.send(_PROTOCOL_CMDS["REPORT_MODE"] % (
            chr(self._report_mode), chr(self._read_count), chr(self._read_delay)))

    def add_input(self, port):
        if port in self._anlg_outputs or port in self._digital_outputs:
            raise ProtocolSetupException("Pin %s is configured as output!" % self.__get_arduino_pin(port))

        self.__validate_pin(port)

        # Determines if we are setting as input an analog port
        if port not in self._anlg_inputs and port in self._board["ANALOG_PINS"]:
            self._anlg_inputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_INPUT"] % chr(port))
            self.__set_pin_mode(port, PIN_MODES.INPUT)

        # Determines if we are setting as input a Digital port
        if port not in self._digital_inputs and port in self._board["DIGITAL_PINS"]:
            self._digital_inputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_INPUT"] % chr(port))
            self.__set_pin_mode(port, PIN_MODES.INPUT)

    def add_output(self, port):
        if port in self._anlg_inputs or port in self._digital_inputs:
            raise ProtocolSetupException("Pin %s is configured as input!" % self.__get_arduino_pin(port))

        self.__validate_pin(port)

        if port not in self._anlg_outputs and port in self._board["ANALOG_PINS"]:
            self._anlg_outputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_OUTPUT"] % chr(port))
            self.__set_pin_mode(port, PIN_MODES.OUTPUT)

        # Determines if we are setting as input a Digital port
        if port not in self._digital_outputs and port in self._board["DIGITAL_PINS"]:
            self._digital_outputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_OUTPUT"] % chr(port))
            self.__set_pin_mode(port, PIN_MODES.OUTPUT)

    def __validate_pin(self, pin):
        if pin not in self._board["DIGITAL_PINS"] and pin not in self._board["ANALOG_PINS"]:
            raise ValueError("Invalid pin %s for board %s" %
                            (pin, self._board["NAME"]))

    def __get_arduino_pin_id(self, pin):
        ret = pin
        if pin in self._board["DIGITAL_PINS"]:
            ret = "D{0}".format(pin)

        if pin in self._board["ANALOG_PINS"]:
            ret = "A{0}".format(pin - len(self._board["DIGITAL_PINS"]))

        return ret

    def reset(self):
        self._connection.send(_PROTOCOL_CMDS["RESET"])
        self._anlg_outputs = []
        self._digital_outputs = []

    def actuate(self, data):
        """
        Actuate over the parametrized output pins
        All the ports must has been configured as output!

        arguments:
        data -- port & value set to actuate
        """
        payload = ""
        size = 0

        # Sets as payload every digital or analog port
        for i in data:
            if i[0] not in self._anlg_outputs and i[0] not in self._digital_outputs:
                pin = self.__get_arduino_pin_id(i[0])
                raise ProtocolSetupException("Port %s not configured as output!" % pin)
            if i[0] in self._anlg_outputs:
                payload = "".join(
                    [payload, chr(i[0]), chr((i[1] & 0xFF00) >> 8), chr(i[1] & 0x00FF)])
                size += 3
            if i[0] in self._digital_outputs:
                payload = "".join([payload, chr(i[0]), chr(i[1])])
                size += 2

        self._connection.send(
            "".join([_PROTOCOL_CMDS["ACTUATE"], chr((size & 0xFF000000) >> 24), chr((size & 0x00FF0000) >> 16),
                     chr((size & 0x0000FF00) >> 8), chr(size & 0x000000FF), payload]))
        #FIXME catch connection exceptions
        response = self._connection.recv(1)

        if response == _PROTOCOL_CMDS["ACK"]:
            response = self._connection.recv(4) # Clears buffer
            raise ProtocolIOException("Actuate error. Code: %s" % response)

        if response != _PROTOCOL_CMDS["ACTUATE_REPORT"]:
            response = self._connection.recv(4)
            raise ProtocolIOException(
                "Actuate error. Unknown response %s after actuate operation" % ord(response))
        # FIXME catch connection exceptions
        raw_len = self._connection.recv(4)
        length = (ord(raw_len[0]) << 24) + (ord(raw_len[1]) << 16) + (ord(raw_len[2]) << 8) + ord(raw_len[3])
        # FIXME catch connection exceptions
        data = self._connection.recv(length)

        pos = 0
        digital_res = {"D%d" % (x): [] for x in self._digital_inputs}
        analog_res = {"A%d" % (x - len(self._board["DIGITAL_PINS"])): [] for x in self._anlg_inputs}
        # results = {x: []
        # for x in self._anlg_inputs + self._digital_inputs}  # One dictionary
        # to save all ports results

        results = dict(digital_res.items() + analog_res.items())

        while pos < length:
            pin = ord(data[pos])
            if pin in self._anlg_inputs:
                for i in range(0, self._read_count + 1):
                    results["A%d" % (pin - len(self._board["DIGITAL_PINS"]))].append(
                        (ord(data[pos + 1]) << 8) + ord(data[pos + 2]))
                    pos = pos + 2
                pos = pos + 1

                if self._report_mode == REPORT_MODES.AVERAGE:
                    results["A%d" % (pin - len(self._board["DIGITAL_PINS"]))] = [
                        sum(results["A%d" % (pin - len(self._board["DIGITAL_PINS"]))]) / (self._read_count + 1)]
            else:
                if pin in self._digital_inputs:
                    for i in range(0, self._read_count + 1):
                        results["D%d" % (pin)].append(
                            bool(ord(data[pos + 1 + i / 8]) & (0x01 << (i % 8))))
                    pos = pos + 1 + self._read_count / 8 + 1

                    if self._report_mode == REPORT_MODES.AVERAGE:
                        results["D%d" % (pin)] = [
                            (sum(results["D%d" % (pin)]) * 2) > (self._read_count + 1)]

                else:
                    raise ProtocolIOException(
                        "Unknown port \"%d\" in response. Please, restart the Arduino board and the experiment." % pin)

        return results


class ProtocolConfig(
    namedtuple('ProtocolConfig', ['connection', 'report_mode', 'read_count', 'read_delay', 'board_type',
                                  'digital_input_pins', 'digital_output_pins', 'analog_input_pins',
                                  'analog_output_pins', 'pwm_pins', 'analog_resolution'])):
    def __new__(cls, connection, report_mode=REPORT_MODES.AVERAGE, read_count=2, read_delay=0, board_type=boards.Due,
                digital_input_pins=None, digital_output_pins=None, analog_input_pins=None, analog_output_pins=None,
                pwm_pins=None, analog_resolution=None):
        digital_input_pins = [] if digital_input_pins is None else digital_input_pins
        digital_output_pins = [] if digital_output_pins is None else digital_output_pins
        analog_input_pins = [] if analog_input_pins is None else analog_input_pins
        analog_output_pins = [] if analog_output_pins is None else analog_output_pins
        pwm_pins = [] if pwm_pins is None else pwm_pins
        analog_resolution = boards.Due["ANALOG_DEFAULT_RESOLUTION"] if analog_resolution is None else analog_resolution

        return super(ProtocolConfig, cls).__new__(cls, connection, report_mode, read_count, read_delay,
                                                  board_type, digital_input_pins, digital_output_pins,
                                                  analog_input_pins, analog_output_pins, pwm_pins, analog_resolution)


def BuildSerial(protocol_config):
    interface = ArduinoInterface(protocol_config.connection, protocol_config.board_type)
    interface.reset()
    interface.set_report_mode(protocol_config.report_mode, protocol_config.read_count, protocol_config.read_delay)

    interface.set_precision(protocol_config.analog_resolution)

    for port in protocol_config.digital_input_pins:
        interface.add_input(port)

    for port in protocol_config.analog_input_pins:
        interface.add_input(port)

    for port in protocol_config.digital_output_pins:
        interface.add_output(port)

    for port in protocol_config.analog_output_pins:
        interface.add_output(port)

    interface.set_precision(protocol_config.analog_resolution)

    return interface
