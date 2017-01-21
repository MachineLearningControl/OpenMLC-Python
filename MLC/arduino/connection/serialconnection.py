from base import BaseConnection
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

        args["baudrate"] = 115200 if not "baudrate" in args.keys() else args["baudrate"]
        args["parity"] = serial.PARITY_NONE if not "parity" in args.keys() else args["parity"]
        args["stopbits"] = serial.STOPBITS_ONE if not "stopbits" in args.keys() else args["stopbits"]
        args["bytesize"] = serial.EIGHTBITS if not "bytesize" in args.keys() else args["bytesize"]
        
        self._connection = serial.Serial(**args); 
        
    
    def send(self, data):
        self._connection.write(data)

    def recv(self, length):
        """ Receives the specified amount of bytes
        WARNING: This function is blocked until receive the amount of bytes
        
        Keyword arguments:
        length -- amount of bytes to receive
        """
        return self._connection.read(length)
