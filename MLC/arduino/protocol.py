
_PROTOCOL_CMDS = {  "ANALOG_PRECISION": '\x01\x01%s',
                    "ANALOG_INPUT"    : '\x02\x01%s',
                    "ANALOG_OUTPUT"   : '\x03\x01%s',
                    "PIN_MODE"        : '\x04\x02%s%s',
                    "REPORT_MODE"     : '\x05\x03%s%s%s',
                    "ACK"             : '\xFF\x00',
                    "ACTUATE"         : '\xF0%s',
                    "ACTUATE_REPORT"  : '\xF1' }

class ArduinoInterface:
    PIN_MOD = {"INPUT":0, "OUTPUT":1} # 0=input 1=output -- wiring_constants.h
    REPORT_MOD = {"AVERAGE":0, "BULK":1, "RT":2}

    def __init__(self, connection):
        self._connection = connection
        self._anlg_inputs = []
        self._anlg_outputs = []
        self._anlg_precition = 10 #Default Arduino analog precition

    def set_precition(self, bits):
        if bits > 32 or bits < 1:
            raise Exception("Precision bits must be between 1 and 32!")
        self._connection.send(_PROTOCOL_CMDS["ANALOG_PRECISION"] % chr(bits))
        self._anlg_precition = bits

    def set_pin_mode(self, port, mode):
        if mode not in self.PIN_MOD.keys():
            raise Exception("Pind mode error. Unknown mode: %s. Modes availables: %s " % (mode, str(PIN_MOD.keys())))
        
        self._connection.send(_PROTOCOL_CMDS["PIN_MODE"] % (chr(port), chr(self.PIN_MOD[mode])))

    def set_report_mode(self, mode, read_count=1, read_delay=0):
        if mode not in self.REPORT_MOD.keys():
            raise Exception("Report mode error. Unknown value: %s" % mode)
        
        self._connection.send(_PROTOCOL_CMDS["REPORT_MODE"] % (chr(self.REPORT_MOD[mode]), chr(read_count), chr(read_delay)))
       
    
    def add_analog_input(self, port):
        if port in self._anlg_outputs:
            raise Exception("Port %s is configured as output!" % port)

        if port not in self._anlg_inputs:
            self._connection.send(_PROTOCOL_CMDS["ANALOG_INPUT"] % chr(port))
            self._anlg_inputs.append(port)

    def add_analog_output(self, port):
        if port in self._anlg_inputs:
            raise Exception("Port %s is configured as input!" % port)

        if port not in self._anlg_outputs:
            self._connection.send(_PROTOCOL_CMDS["ANALOG_OUTPUT"] % chr(port))
            self._anlg_outputs.append(port)

    def actuate(self, data):
        """
        Actuate over the input port sent as parameters
        All the ports must has been configured as output!

        arguments:
        data -- port & value set to actuate
        """
        payload = ""
        size = 0
        #TODO: Ver como validar puertos digitales
        for i in data:
            if i[0] not in self._anlg_outputs:
                raise Exception("Port %s not configured as output!" % i[0])
            payload = "".join([payload, chr(i[0]), chr((i[1] & 0xFF00) >> 8), chr(i[1] & 0x00FF)])
            size += 3 

        self._connection.send("".join([_PROTOCOL_CMDS["ACTUATE"], chr(size), payload]))
        response = self._connection.recv(1)

        if response == _PROTOCOL_CMDS["ACK"]:
            response = self._connection.recv(1)
            raise Exception("Actuate error. Code: %s" % response)

        if response <> _PROTOCOL_CMDS["ACTUATE_REPORT"]:
            raise Exception("Actuate error. Unknown response %s after actuate operation" % response)

        length = ord(self._connection.recv(1))
        data = self._connection.recv(length)

        pos = 0
        results = []
        while pos < length:
            if ord(data[pos]) in self._anlg_inputs:
                results.append((data[pos], (ord(data[pos+1]) << 8) + ord(data[pos+2])))
                pos = pos + 3
            else:
                results.append((data[pos], bool(ord(data[pos+1]))))
                pos = pos + 2

        return results
        
