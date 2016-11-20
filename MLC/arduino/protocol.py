
_PROTOCOL_CMDS = {  "ANALOG_PRECISION": '\x01\x01%s',
                    "SET_INPUT"    : '\x02\x01%s',
                    "SET_OUTPUT"   : '\x03\x01%s',
                    "PIN_MODE"        : '\x04\x02%s%s',
                    "REPORT_MODE"     : '\x05\x03%s%s%s',
                    "ACK"             : '\xFF\x00',
                    "ACTUATE"         : '\xF0',
                    "RESET"           : '\xFE',
                    "ACTUATE_REPORT"  : '\xF1' }

class ArduinoInterface:
    PIN_MOD = {"INPUT":0, "OUTPUT":1} # 0=input 1=output -- wiring_constants.h
    REPORT_MOD = {"AVERAGE":0, "BULK":1, "RT":2}

    def __init__(self, connection, board):
        self._connection = connection
        self._anlg_inputs = []
        self._digital_inputs = []
        self._anlg_outputs = []
        self._digital_outputs = []
        self._anlg_precition = 10 #Default Arduino analog precision
        self._report_mode = "AVERAGE"
        self._read_count = 1 #Default number of inputs read
        self._read_delay = 0
        self._board = board

    def set_precition(self, bits):
        if bits > 32 or bits < 1:
            raise Exception("Precision bits must be between 1 and 32!")
        self._connection.send(_PROTOCOL_CMDS["ANALOG_PRECISION"] % chr(bits))
        self._anlg_precition = bits

    def __set_pin_mode(self, port, mode):
        if mode not in self.PIN_MOD.keys():
            raise Exception("Pind mode error. Unknown mode: %s. Modes availables: %s " % (mode, str(self.PIN_MOD.keys())))
        
        self._connection.send(_PROTOCOL_CMDS["PIN_MODE"] % (chr(port), chr(self.PIN_MOD[mode])))

    def set_report_mode(self, mode, read_count=0, read_delay=0):
        if mode not in self.REPORT_MOD.keys():
            raise Exception("Report mode error. Unknown value: %s" % mode)

        self._report_mode = mode
        self._read_count = read_count + 1
        self._read_delay = read_delay
        
        self._connection.send(_PROTOCOL_CMDS["REPORT_MODE"] % (chr(self.REPORT_MOD[mode]), chr(read_count), chr(read_delay)))
  
    
    def add_input(self, port):
        if port in self._anlg_outputs or port in self._digital_outputs:
            raise Exception("Pin %s is configured as output!" % port)
   
        self.__validate_pin(port)
        self._connection.send(_PROTOCOL_CMDS["SET_INPUT"] % chr(port))
        self.__set_pin_mode(port, "INPUT")

        # Determines if we are setting as input an analog port
        if port not in self._anlg_inputs and port in self._board["ANALOG_PINS"]:
            self._anlg_inputs.append(port)

        # Determines if we are setting as input a Digital port
        if port not in self._digital_inputs and port in self._board["DIGITAL_PINS"]:
            self._digital_inputs.append(port)
            

    def add_output(self, port):
        if port in self._anlg_inputs or port in self._digital_inputs:
            raise Exception("Port %s is configured as input!" % port)

        self.__validate_pin(port)
        self._connection.send(_PROTOCOL_CMDS["SET_OUTPUT"] % chr(port))
        self.__set_pin_mode(port, "OUTPUT")

        if port not in self._anlg_outputs and port in self._board["ANALOG_PINS"]:
            self._anlg_outputs.append(port)

        # Determines if we are setting as input a Digital port
        if port not in self._digital_outputs and port in self._board["DIGITAL_PINS"]:
            self._digital_outputs.append(port)

    def __validate_pin(self, pin):
        if pin not in self._board["DIGITAL_PINS"] and pin not in self._board["ANALOG_PINS"]:
            raise Exception("Invalid pin %s for board %s" % (pin, self._board["NAME"]))
        return
  
    def reset(self):
        self._connection.send(_PROTOCOL_CMDS["RESET"])

    def actuate(self, data):
        """
        Actuate over the parametrized output pins
        All the ports must has been configured as output!

        arguments:
        data -- port & value set to actuate
        """
        payload = ""
        size = 0

        # Sets as payload every digital or analog port
        for i in data:
            if i[0] not in self._anlg_outputs and i[0] not in self._digital_outputs:
                raise Exception("Port %s not configured as output!" % i[0])
            if i[0] in self._anlg_outputs:
                payload = "".join([payload, chr(i[0]), chr((i[1] & 0xFF00) >> 8), chr(i[1] & 0x00FF)])
                size += 3
            if i[0] in self._digital_outputs:
                payload = "".join([payload, chr(i[0]), chr(i[1])])
                size += 2

        self._connection.send("".join([_PROTOCOL_CMDS["ACTUATE"], chr(size), payload]))
        response = self._connection.recv(1)

        if response == _PROTOCOL_CMDS["ACK"]:
            response = self._connection.recv(1)
            raise Exception("Actuate error. Code: %s" % response)

        if response <> _PROTOCOL_CMDS["ACTUATE_REPORT"]:
            raise Exception("Actuate error. Unknown response %s after actuate operation" % ord(response))

        length = ord(self._connection.recv(1))
        data = self._connection.recv(length)

        pos = 0
        results = []
        while pos < length:
            if ord(data[pos]) in self._anlg_inputs:
                results.append((data[pos], (ord(data[pos+1]) << 8) + ord(data[pos+2])))
                pos = pos + 3
            else:
                if ord(data[pos]) in self._digital_inputs:
                    for i in range(0, self._read_count):
                        results.append((data[pos], bool(ord(data[pos+1]))))
                    pos = pos + 2
                else:
                    raise Exception("Unknown port in response. Restart Arduino board, your software and pray")

        return results
        
