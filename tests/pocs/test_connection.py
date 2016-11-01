#from MLC.arduino.connection import MockConnection
from MLC.arduino.connection import SerialConnection
from MLC.arduino.protocol import ArduinoInterface
from MLC.arduino import boards
import sys
import time

def actuate(terminal):
    connection = SerialConnection(port=terminal)
    arduinoDue = ArduinoInterface(connection, boards.Due)
    
    arduinoDue.add_output(40)
    arduinoDue.add_input(64)

    output = arduinoDue.actuate([(40,1)])
    for i in output:
        print "Pin %d output: %s" % (ord(i[0]), i[1])


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "Usage: test_connection.py /dev/ttyACMX (X == number)"
        exit(-1)
    actuate(sys.argv[1:][0])

