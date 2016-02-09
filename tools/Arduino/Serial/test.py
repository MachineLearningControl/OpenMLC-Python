#! /usr/bin/python2.7
import serial
import time

def main():
    ser = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=2.0)
    time.sleep(1)
    print "PRENDIENDO ALARMA DE QUE ESTA TODO BIEN!!"
    ser.write('1|1000000|0.10\n')
    response = ser.readline()
    print response

if __name__ == "__main__":
    main()

