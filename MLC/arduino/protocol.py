import collections

_PROTOCOL_CMDS = {"ANALOG_PRECISION": '\x01\x01%s',
                  "SET_INPUT": '\x02\x01%s',
                  "SET_OUTPUT": '\x03\x01%s',
                  "PIN_MODE": '\x04\x02%s%s',
                  "REPORT_MODE": '\x05\x03%s%s%s',
                  "ANALOG_WRITE": '\x06\x03%s%s%s',
                  "ACK": '\xFF\x00',
                  "ACTUATE": '\xF0',
                  "PROT_VERSION": '\xF2\x00',
                  "RESET": '\xFE',
                  "ACTUATE_REPORT": '\xF1'}


REPORT_MODES = collections.namedtuple(
    'PIN', ['AVERAGE', 'BULK', 'RT'], verbose=False)(AVERAGE=0, BULK=1, RT=2)
PIN_MODES = collections.namedtuple(
    'REPORT', ['INPUT', 'OUTPUT'], verbose=False)(INPUT=0, OUTPUT=1)


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
            raise Exception("Port %s is configured as input!" % port)

        self._connection.send(_PROTOCOL_CMDS["ANALAOG_WRITE"] % (
            chr(pin), chr((duty_cicle & 0xFF00) >> 8), chr(duty_cicle & 0x00FF)))

    def set_precision(self, bits):
        if bits > 32 or bits < 1:
            raise Exception("Precision bits must be between 1 and 32!")
        self._connection.send(_PROTOCOL_CMDS["ANALOG_PRECISION"] % chr(bits))
        self._anlg_precition = bits

    def __set_pin_mode(self, port, mode):
        if mode not in PIN_MODES._asdict().values():
            raise Exception("Pind mode error. Unknown mode: %s. Modes availables: %s " %
                            (mode, str(PIN_MODES_asdict().keys())))

        self._connection.send(
            _PROTOCOL_CMDS["PIN_MODE"] % (chr(port), chr(mode)))

    def set_report_mode(self, mode, read_count=1, read_delay=0):
        if mode not in REPORT_MODES._asdict().values():
            raise Exception("Report mode error. Unknown value: %s" % mode)

        if read_count <= 0:
            raise Exception("Read count value must be > 0")

        self._report_mode = mode
        self._read_count = read_count - 1
        self._read_delay = read_delay

        self._connection.send(_PROTOCOL_CMDS["REPORT_MODE"] % (
            chr(self._report_mode), chr(self._read_count), chr(self._read_delay)))

    def add_input(self, port):
        if port in self._anlg_outputs or port in self._digital_outputs:
            raise Exception("Pin %s is configured as output!" % port)

        self.__validate_pin(port)

        # Determines if we are setting as input an analog port
        if port not in self._anlg_inputs and port in self._board["ANALOG_PINS"]:
            self._anlg_inputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_INPUT"] % chr(port))
            self.__set_pin_mode(port, REPORT_MODES.INPUT)

        # Determines if we are setting as input a Digital port
        if port not in self._digital_inputs and port in self._board["DIGITAL_PINS"]:
            self._digital_inputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_INPUT"] % chr(port))
            self.__set_pin_mode(port, REPORT_MODES.INPUT)

    def add_output(self, port):
        if port in self._anlg_inputs or port in self._digital_inputs:
            raise Exception("Port %s is configured as input!" % port)

        self.__validate_pin(port)

        if port not in self._anlg_outputs and port in self._board["ANALOG_PINS"]:
            self._anlg_outputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_OUTPUT"] % chr(port))
            self.__set_pin_mode(port, REPORT_MODES.OUTPUT)

        # Determines if we are setting as input a Digital port
        if port not in self._digital_outputs and port in self._board["DIGITAL_PINS"]:
            self._digital_outputs.append(port)
            self._connection.send(_PROTOCOL_CMDS["SET_OUTPUT"] % chr(port))
            self.__set_pin_mode(port, REPORT_MODES.OUTPUT)

    def __validate_pin(self, pin):
        if pin not in self._board["DIGITAL_PINS"] and pin not in self._board["ANALOG_PINS"]:
            raise Exception("Invalid pin %s for board %s" %
                            (pin, self._board["NAME"]))

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
                raise Exception("Port %s not configured as output!" % i[0])
            if i[0] in self._anlg_outputs:
                payload = "".join(
                    [payload, chr(i[0]), chr((i[1] & 0xFF00) >> 8), chr(i[1] & 0x00FF)])
                size += 3
            if i[0] in self._digital_outputs:
                payload = "".join([payload, chr(i[0]), chr(i[1])])
                size += 2

        self._connection.send(
            "".join([_PROTOCOL_CMDS["ACTUATE"], chr(size), payload]))
        response = self._connection.recv(1)

        if response == _PROTOCOL_CMDS["ACK"]:
            response = self._connection.recv(1)
            raise Exception("Actuate error. Code: %s" % response)

        if response != _PROTOCOL_CMDS["ACTUATE_REPORT"]:
            raise Exception(
                "Actuate error. Unknown response %s after actuate operation" % ord(response))

        length = ord(self._connection.recv(1))
        data = self._connection.recv(length)

        pos = 0
        digital_res = {"D%d" % (x): [] for x in self._digital_inputs}
        analog_res = {"A%d" % (x): [] for x in self._anlg_inputs}
        # results = {x: []
        # for x in self._anlg_inputs + self._digital_inputs}  # One dictionary
        # to save all ports results

        results = dict(digital_res.items() + analog_res.items())

        while pos < length:
            pin = ord(data[pos])
            if pin in self._anlg_inputs:
                for i in range(0, self._read_count + 1):
                    results["A%d" % (pin)].append(
                        (ord(data[pos + 1]) << 8) + ord(data[pos + 2]))
                    pos = pos + 2
                pos = pos + 1

                if self._report_mode == "AVERAGE":
                    results["A%d" % (pin)] = [
                        sum(results["A%d" % (pin)]) / (self._read_count + 1)]
            else:
                if pin in self._digital_inputs:
                    for i in range(0, self._read_count + 1):
                        results["D%d" % (pin)].append(
                            bool(ord(data[pos + 1 + i / 8]) & (0x01 << (i % 8))))
                    pos = pos + 1 + self._read_count / 8 + 1

                    if self._report_mode == "AVERAGE":
                        results["D%d" % (pin)] = [
                            (sum(results["D%d" % (pin)]) * 2) > (self._read_count + 1)]

                else:
                    raise Exception(
                        "Unknown port \"%d\" in response. Restart Arduino board, your software and pray" % pin)

        return results

import boards
from collections import namedtuple


class ProtocolConfig (namedtuple('ProtocolConfig', ['connection', 'report_mode', 'read_count', 'read_delay', 'board_type', 'digital_input_pins', 'digital_output_pins', 'analog_input_pins', 'analog_output_pins', 'pwm_pins'])):

    def __new__(cls, connection, report_mode=REPORT_MODES.AVERAGE, read_count=2, read_delay=0, board_type=boards.Due, digital_input_pins=[], digital_output_pins=[], analog_input_pins=[], analog_output_pins=[], pwm_pins=[]):
        return super(ProtocolConfig, cls).__new__(cls, connection, report_mode, read_count, read_delay, board_type, digital_input_pins, digital_output_pins, analog_input_pins, analog_output_pins, pwm_pins)


def BuildSerial(protocol_config):
    interface = ArduinoInterface(
        protocol_config.connection, protocol_config.board_type)
    interface.reset()
    interface.set_report_mode(
        protocol_config.report_mode, protocol_config.read_count, protocol_config.read_delay)

    for port in protocol_config.digital_input_pins:
        interface.add_input(port)

    for port in protocol_config.analog_input_pins:
        interface.add_input(port)

    for port in protocol_config.digital_output_pins:
        interface.add_output(port)

    for port in protocol_config.analog_output_pins:
        interface.add_output(port)

    return interface
