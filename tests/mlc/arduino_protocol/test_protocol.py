import unittest
from MLC.arduino.connection import MockConnection
from MLC.arduino.protocol import ArduinoInterface
from MLC.arduino import boards

ACK = "\xFF\x00"
NACK = "\xFF\x01"
REPORT = "\xF1\x05\x10\x01\x3D\x05\x20"
REPORT_B = "\xF1\x1A\x10\xF1\x0A\x3D\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00"
REPORT_C = "\xF1\x16\x3D\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x3E\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00"


class TestArduinoInterface(unittest.TestCase):

    def setUp(self):
        self._connection = MockConnection(ACK)
        self._interface = ArduinoInterface(self._connection, boards.Due)
    
    def test_set_precition(self):
        self._interface.set_precision(12)
        data = self._connection.pop_data()
        self.assertEqual("\x01\x01\x0C", data)
        with self.assertRaises(Exception):
            self._interface.set_precition(33)

    def test_report_mode(self):
        self._interface.set_report_mode("AVERAGE")
        data = self._connection.pop_data()
        self.assertEqual("\x05\x03\x00\x00\x00", data)
        self._interface.set_report_mode("AVERAGE", read_count=10, read_delay=5)
        data = self._connection.pop_data()
        self.assertEqual("\x05\x03\x00\x09\x05", data)
        with self.assertRaises(Exception):
            self._interface.set_report_mode("SOMETHING")

    def test_add_input(self):
        self._interface.add_input(60)
        data = self._connection.pop_data()
        self.assertEqual("\x02\x01\x3C", data)
        data = self._connection.pop_data()
        self.assertEqual("\x04\x02\x3C\x00", data)
        self._interface.add_input(60)
        with self.assertRaises(Exception):  # Checks that no data has been sent
            data = self._connection.pop_data()
        with self.assertRaises(Exception):  # Checks that no data has been sent
            self._interface.add_output(128)

    def test_add_output(self):
        self._interface.add_output(60)
        data = self._connection.pop_data()
        self.assertEqual("\x03\x01\x3C", data)
        data = self._connection.pop_data()
        self.assertEqual("\x04\x02\x3C\x01", data)
        self._interface.add_output(60)
        with self.assertRaises(Exception):  # Checks that no data has been sent
            data = self._connection.pop_data()
        with self.assertRaises(Exception):  # Checks that no data has been sent
            self._interface.add_output(128)
        
    def test_error_adding_output_that_is_input(self):
        self._interface.add_input(60)
        with self.assertRaises(Exception): 
            self._interface.add_analog_output(60)
             
    def test_actuate_error_response(self):
        self._interface.add_output(60)
        self._connection.pop_data()
        with self.assertRaises(Exception): 
            self._interface.actuate([(60, 128)])

    def test_actuate_with_one_read(self):
        self._connection = MockConnection(REPORT)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.add_output(60)
        self._interface.add_input(16)
        self._interface.add_input(61)
        response = self._interface.actuate([(60, 128)])
        self.assertEqual(1, len(response[0x10]))
        self.assertTrue(response[0x10][0])
        self.assertEqual(1, len(response[0x3D]))
        self.assertEqual(0x0520,response[0x3D][0])
        
    def test_actuate_with_many_readings(self):
        self._connection = MockConnection(REPORT_B)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.set_report_mode("BULK", read_count=11, read_delay=5)
        self._interface.add_output(60)
        self._interface.add_input(61)
        self._interface.add_input(16)
        response = self._interface.actuate([(60, 128)])
        self.assertEqual(2, len(response))
        self.assertTrue(response[0x10][0])
        self.assertTrue(response[0x10][6])
        self.assertTrue(response[0x10][7])
        self.assertFalse(response[0x10][8])
        self.assertTrue(response[0x10][9])
        self.assertFalse(response[0x10][10])
        for i in range(0, 11):
           self.assertEqual(0x0100, response[0x3D][i])

    def test_actuate_with_many_pins_readings(self):
        self._connection = MockConnection(REPORT_C)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.set_report_mode("BULK", read_count=5, read_delay=5)
        self._interface.add_output(60)
        self._interface.add_input(61)
        self._interface.add_input(62)
        response = self._interface.actuate([(60, 128)])
        for i in range(0, 5):
           self.assertEqual(0x0100, response[0x3D][i])
        for i in range(0, 5):
           self.assertEqual(0x0100, response[0x3E][i])


    def test_average(self):
        self._connection = MockConnection(REPORT_B)
        self._interface = ArduinoInterface(self._connection, boards.Due)
        self._interface.set_report_mode("AVERAGE", read_count=11, read_delay=5)
        self._interface.add_output(60)
        self._interface.add_input(61)
        self._interface.add_input(16)
        response = self._interface.actuate([(60, 128)])
        self.assertEqual(2, len(response))
        self.assertEqual(1, len(response[0x10]))
        self.assertTrue(response[0x10][0])
        self.assertEqual(0x0100, response[0x3D][0])
        
                
