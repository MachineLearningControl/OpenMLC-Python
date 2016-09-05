import time
import serial
import struct

RW_OPERATIONS=300000


'''
Test I/O operations using Serial connection to the arduino

Setting as port the ArduinoDUE native USB (and loading the related test script in the ArduinoDUE board)
this scripts test how many write/read operations per second are allowed but this port.

The output of the script is print on stdout. The RW_OPERATIONS var sets the the max number of R/W op.
to accomplish in order to finalize the test.
'''

ser = serial.Serial(
   port='/dev/ttyACM0',
   baudrate=115200,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS
)

WRITE_DATA="123456789012" # Data to send to the Arduino

best = 1000;
worst = 0;
read_c = 0;

last_time = time.time()
start_time = last_time
for i in range(1,RW_OPERATIONS):
    ser.write(WRITE_DATA)
    data = ser.read(4); # The data send by the Arduino must have a length byte. This is mandatory due 
                        # that serial read blocks until it has read the specified count of bytes
    n = struct.unpack("<L", data)[0]; # Gets long representation
    data = ser.read(n);
    new_time = time.time()
    get_time = new_time - last_time
    #print 'Operation delay in ' + str(get_time) + ' seconds'
    read_c = read_c + 1
    
    if new_time-last_time < best:
       best = get_time

    if new_time-last_time > worst:
       worst = get_time
    
    if (new_time - start_time) > 1:
       print str(read_c-1) # The current read was out of the period
       read_c = 1
       start_time = new_time
    
    #print 'best: ' + str(best) + ' worst: ' + str(worst)
    last_time = new_time
