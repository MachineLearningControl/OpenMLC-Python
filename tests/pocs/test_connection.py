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

    last_time = time.time()
    start_time = last_time
    read_c = 0

    for i in range(0, 100000):
        arduinoDue.actuate([(40,1)])
        read_c = read_c + 1
        new_time = time.time()

        if (new_time - start_time) > 1:
           print str(read_c-1) # The current read was out of the period
           read_c = 1
           start_time = new_time

        last_time = new_time


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "Usage: test_connection.py /dev/ttyACMX (X == number)"
        exit(-1)
    actuate(sys.argv[1:][0])

