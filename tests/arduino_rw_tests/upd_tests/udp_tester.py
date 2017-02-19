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

IP = "192.168.1.177"
PORT = 5000 # Para udp en arduino cualquier puerto sirve 

R_W_COUNT = 30000 # Cantidad de operaciones de I/O a realizar

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0',PORT))

read_c = 0;

last_time = time.time()
start_time = last_time

for i in range(1, R_W_COUNT):
  sock.sendto("123456789012", (IP, PORT))
  data, addr = sock.recvfrom(1500);
  new_time = time.time()
  read_c = read_c + 1

  if (new_time - start_time) > 1:
     print str(read_c-1)
     read_c = 1
     start_time = new_time

  
  


