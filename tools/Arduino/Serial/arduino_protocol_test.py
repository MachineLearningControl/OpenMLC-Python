#! /usr/bin/python2.7
import serial
import time
from struct import *

def main():
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=2.0)
    time.sleep(1)
    print "PRENDIENDO ALARMA DE QUE ESTA TODO BIEN!!"

    port1 = 10
    port2 = 8
    # Start configuration 
    send_command(ser, pack('BB', 1, 2))

    # Set port 10 as output
    send_command(ser, pack('BB', 10, 6))
    send_command(ser, pack('BBBB', port1, 2, port2, 2)) 

    # End configuration
    send_command(ser, pack('BB', 2, 2))

    # Turn on port 8 and 4
    send_command(ser, pack('BB', 20, 4))
    send_command(ser, pack('BB', port1, 1))
    time.sleep(5)

    # Toggle ports
    send_command(ser, pack('BB', 20, 6))
    send_command(ser, pack('BBBB', port1, 0, port2, 1))
    time.sleep(5)

    # Turn both
    send_command(ser, pack('BB', 20, 6))
    send_command(ser, pack('BBBB', port1, 1, port2, 1))
    time.sleep(5)

    # Turn off both leds
    send_command(ser, pack('BB', 20, 6))
    send_command(ser, pack('BBBB', port1, 0, port2, 0))

def send_command(ser, cmd):
    ser.write(cmd)
    while ser.inWaiting() < 4:
        continue

    bytesToRead = ser.inWaiting()
    bytesRead = ser.read(bytesToRead)
    response = unpack("B" * bytesToRead, bytesRead)

    if response is not None:
        print response

    if response[0] != 3:
        raise RuntimeError

if __name__ == "__main__":
    main()

