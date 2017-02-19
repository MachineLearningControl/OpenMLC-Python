#!/usr/bin/python
# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import socket
import time
import sys

COUNT=1000
ARDUINO_SERVER = ('192.168.1.177', 80)
BUFF = 1000
ITERATIONS = 800
DATA_MULTIPLIER = 3

def send_recv(s, start_t, epoch_time, send_count, loop):
   s.send("a"*send_count + "\n\n")
   readings = s.recv(BUFF)
   data_rcv = len(readings)
   speed = data_rcv/(time.time()-start_t)
   connections = loop / (time.time() - epoch_time)
   #print "In " + str(loop) + " Data rcv: " + str((data_rcv)) + " Speed: "+ str(speed) + "B/s" + " Connections: " + str(connections) + "Conn/s" + '\r'
   print str(loop) + "," + str((speed)) + "," + str(connections)
   time.sleep(0.0001)

def open_close_test(send_count):
    print "Iniciando test de conexion no continua con envio de " + str(send_count) + " bytes"
    epoch_time = time.time()
    data_rcv = 0
    loop = 0
    for i in range(0,ITERATIONS):
        start_t = time.time()
        s = socket.socket()
        s.connect(ARDUINO_SERVER)
        loop = loop + 1
	send_recv(s, start_t, epoch_time, send_count, loop)
        s.close()

def keep_alive_test(send_count):
    print "Iniciando test de conexion continua con envio de " + str(send_count) + " bytes"
    epoch_time = time.time()
    s = socket.socket()
    s.connect(ARDUINO_SERVER)
    loop = 0
    for i in range(0,ITERATIONS):
        start_t = time.time()
        loop = loop + 1
	send_recv(s, start_t, epoch_time, send_count, loop)
    
    s.close()

test = {"open_close_test": open_close_test, "keep_alive_test": keep_alive_test}

if __name__ == "__main__":
    if(len(sys.argv) <> 2):
	print "Uso: ethernet_tester test_name"
        print "Test disponibles: "
        for test_name in test.keys():
            print "     * " + test_name
        sys.exit(0)
   
    if sys.argv[1] in test.keys():
        for i in range(10,11):
            test[sys.argv[1]](i*DATA_MULTIPLIER)
    else:
        print "Test " + sys.argv[1] + " desconocido." 
        sys.exit(-1)

