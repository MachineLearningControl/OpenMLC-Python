#from MLC.arduino.connection import MockConnection
from MLC.arduino.connection import SerialConnection
from MLC.arduino.protocol import ArduinoInterface
from MLC.arduino import boards
import sys
import time

def actuate(terminal):
    connection = SerialConnection(port=terminal)
    arduinoDue = ArduinoInterface(connection, boards.Due)
    
    arduinoDue.reset() #Just in case
    arduinoDue.set_report_mode("AVERAGE", read_count=1, read_delay=200)
    
    arduinoDue.add_output(40)
    arduinoDue.add_output(66)
#    arduinoDue.add_input(65)
#    arduinoDue.add_input(64)
#    arduinoDue.add_input(63)
#    arduinoDue.add_input(62)
#    arduinoDue.add_input(61)
#    arduinoDue.add_input(60)
#    arduinoDue.add_input(59)
#    arduinoDue.add_input(58)
#    arduinoDue.add_input(57)
#    arduinoDue.add_input(56)
#    arduinoDue.add_input(55)
    arduinoDue.add_input(54)

    last_time = time.time()
    start_time = last_time
    read_c = 0
    
    for i in xrange(0, 2):
        output = arduinoDue.actuate([(40,1),(66,255)])
        #print output
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

