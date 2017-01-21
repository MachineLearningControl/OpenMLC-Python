
class BaseConnection:
    '''
    Connection base class
    
    Defines method for I/O with an Arduino device
    '''
    def send(self,data):
       """ Sends data to arduino device """
       raise Exception("Implement me!")

    def recv(self, length):
       """ Receive data from the arduino device """
       raise Exception("Implement me!") 
