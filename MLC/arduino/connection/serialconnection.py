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

        if recv != length:
            raise serial.SerialTimeoutException
        else:
            return recv

class SerialConnectionConfig (namedtuple('SerialConnectionConfig', ['port', 'baudrate', 'parity', 'stopbits', 'bytesize'])):

    def __new__(cls, port, baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS):
        return super(SerialConnectionConfig, cls).__new__(cls, port, baudrate, parity, stopbits, bytesize)
