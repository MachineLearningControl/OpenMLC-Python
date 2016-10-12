from base import BaseConnection

class MockConnection(BaseConnection):
    """ Connection that save the data sent using "send" method and response 
        on a "recv" call using a pre-configured response buffer
    """
    def __init__(self, responses):
        """ response -- bytes stream of responses that will be used in recv method """
        self._received = []
        self._responses = responses
        self._resp_idx = 0
    
    def send(self, data):
        """ \"sends\" the data to a inner buffer """
        self._received.insert(0,data)

    def pop_data(self):
        """ Pops a complete data stream received """
        return self._received.pop()

    def recv(self, length):
        """
        Looping receiver (if buffer run out of data, it add to the response bytes from the beginning)

        length -- count of bytes to \"receive\"
        """
        pos = self._resp_idx
        if pos + length > len(self._responses):
            self._resp_idx = (length - (len(self._responses)-pos))%len(self._responses)
            return self._responses[pos:] + self._responses[0:length - (len(self._responses)-pos)]

        self._resp_idx = pos + length
        return self._responses[pos:pos+length]

