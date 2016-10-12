import unittest
from MLC.arduino.connection import MockConnection
from MLC.arduino.protocol import ArduinoInterface

ACK = "\xFF\x00"
NACK = "\xFF\x01"
REPORT = "\xF1\x05\x10\x01\x3D\x05\x20"


class TestArduinoInterface(unittest.TestCase):

    def setUp(self):
        self._connection = MockConnection(ACK)
        self._interface = ArduinoInterface(self._connection)
    
    def test_set_precition(self):
        self._interface.set_precition(12)
        data = self._connection.pop_data()
        self.assertEqual("\x01\x01\x0C", data)
        with self.assertRaises(Exception):
            self._interface.set_precition(33)

    def test_set_pin_mode(self):
        self._interface.set_pin_mode(1, "INPUT")
        data = self._connection.pop_data()
        self.assertEqual("\x04\x02\x01\x00", data)
        with self.assertRaises(Exception):
            self._interface.set_pin_mode(1, "SOMETHING")
        
    def test_report_mode(self):
        self._interface.set_report_mode("AVERAGE")
        data = self._connection.pop_data()
        self.assertEqual("\x05\x03\x00\x01\x00", data)
        self._interface.set_report_mode("AVERAGE", read_count=10, read_delay=5)
        data = self._connection.pop_data()
        self.assertEqual("\x05\x03\x00\x0A\x05", data)
        with self.assertRaises(Exception):
            self._interface.set_report_mode("SOMETHING")

    def test_add_analog_input(self):
        self._interface.add_analog_input(60)
        data = self._connection.pop_data()
        self.assertEqual("\x02\x01\x3C", data)
        self._interface.add_analog_input(60)
        with self.assertRaises(Exception):  # Checks that no data has been sent
            data = self._connection.pop_data()

    def test_add_analog_output(self):
        self._interface.add_analog_output(60)
        data = self._connection.pop_data()
        self.assertEqual("\x03\x01\x3C", data)
        self._interface.add_analog_output(60)
        with self.assertRaises(Exception):  # Checks that no data has been sent
            data = self._connection.pop_data()
        
    def test_error_adding_output_that_is_input(self):
        self._interface.add_analog_input(60)
        with self.assertRaises(Exception): 
            self._interface.add_analog_output(60)
             
    def test_actuate_error_response(self):
        self._interface.add_analog_output(60)
        self._connection.pop_data()
        with self.assertRaises(Exception): 
            self._interface.actuate([(60, 128)])

    def test_actuate(self):
        self._connection = MockConnection(REPORT)
        self._interface = ArduinoInterface(self._connection)
        self._interface.add_analog_output(60)
        self._interface.add_analog_input(61)
        response = self._interface.actuate([(60, 128)])
        self.assertEqual(2, len(response))
        self.assertEqual("\x10",response[0][0])
        self.assertTrue(response[0][1])
        self.assertEqual("\x3D",response[1][0])
        self.assertEqual(0x0520,response[1][1])
        
                
