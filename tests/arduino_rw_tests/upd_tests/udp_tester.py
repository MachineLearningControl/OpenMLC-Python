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

  
  


