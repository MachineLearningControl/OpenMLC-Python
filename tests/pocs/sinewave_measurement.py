import matplotlib.pyplot as plt
import sys
import time
sys.path.append("../..")

from MLC.arduino.connection import SerialConnection
from MLC.arduino.protocol import ArduinoInterface
from MLC.arduino import boards

def actuate(terminal):
    connection = SerialConnection(port=terminal)
    arduinoDue = ArduinoInterface(connection, boards.Due)

    arduinoDue.set_precision(12)
    arduinoDue.add_input(54)
    arduinoDue.add_output(40)

    last_time = time.time()
    start_time = last_time
    read_c = 0

    diff = last_time - start_time
    measures = []
    while diff < 10:
        print "Reading... {0}".format(diff)
        results = arduinoDue.actuate([(40,1)])
        measures.append(results)
        last_time = time.time()
        diff = last_time - start_time

    # Process samples
    samples = []
    for element in measures:
        for i in xrange(len(element)):
            samples.append(int(element[i][1]))

    # print "{0}".format(samples)
    print "Samples len: {0}".format(len(samples))

    plt.clf()
    plt.plot(samples)
    plt.show(block=True)

def main():
    actuate("/dev/ttyACM0")

if __name__ == "__main__":
    main()
