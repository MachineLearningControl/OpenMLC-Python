from base import BaseConnection
import serial


class SerialConnection(BaseConnection):
    def __init__(self, **args):
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
        return self._connection.read(length)
