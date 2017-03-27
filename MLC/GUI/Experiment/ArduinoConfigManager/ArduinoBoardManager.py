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

from ArduinoBench import ArduinoBench

from MLC.GUI.Experiment.ArduinoConfigManager.BoardConfigurationWindow import BoardConfigurationWindow
from MLC.arduino import boards
from MLC.arduino.connection.serialconnection import SerialConnection, SerialConnectionConfig
from MLC.arduino.protocol import ProtocolConfig, init_interface
from MLC.arduino.connection.base import ConnectionException, ConnectionTimeoutException

from PyQt5.QtWidgets import QMessageBox

import serial
import threading


class ArduinoBoardManager:

    def __init__(self, protocol_config, serial_config, close_handler, parent_win=None):
        self.__setup = protocol_config
        self.__connection_config = serial_config
        self.__main_window = BoardConfigurationWindow(self, boards.types, self.__setup, parent=parent_win)
        self.__connectino_status = None
        self.PARITY_BITS = [serial.PARITY_NONE, serial.PARITY_EVEN,
                            serial.PARITY_EVEN, serial.PARITY_MARK, serial.PARITY_SPACE]
        self.STOP_BITS = [serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO]
        self.BYTE_SIZE = [serial.EIGHTBITS, serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS]
        # FIXME the connection with the handler shold be made by a method of the window
        self.__main_window.on_close_signal.connect(close_handler)

    def get_protocol_config(self):
        return self.__setup

    def get_connection_config(self):
        current_setup = self.__main_window.checkout_connection_config()
        config = SerialConnectionConfig(port=current_setup["port"],
                                        baudrate=current_setup["baudrate"],
                                        parity=self.PARITY_BITS[current_setup["parity"]],
                                        stopbits=self.STOP_BITS[current_setup["stopbits"]],
                                        bytesize=self.BYTE_SIZE[current_setup["bytesize"]])
        return config

    def start_connection(self):
        # TODO Este metodo debe estar enlazado a la opcion de conexion serie
        self.__connection_config = self.get_connection_config()

        return SerialConnection(**self.__connection_config._asdict())

    def start(self):
        self.__main_window.show()

    def insert_digital_pin(self, pin_index, pin, type_idx):
        if pin_index < 0:
            return

        current = self.__main_window.get_current_board()["DIGITAL_PINS"] if type_idx != 2 else \
            self.__main_window.get_current_board()["PWM_PINS"]
        target_pin = self.__setup.digital_input_pins if type_idx == 0 else \
            self.__setup.digital_output_pins if type_idx == 1 else self.__setup.pwm_pins

        if pin in current and pin not in self.__setup.digital_input_pins and pin not in self.__setup.digital_output_pins \
           and pin not in self.__setup.pwm_pins:
            target_pin.append(pin)
            self.__main_window.addDigitalPin(pin_index, type_idx)
        else:
            self.show_error(
                "Error", "Assign error", "Could not set pin %s with the selected type" % (pin),
                QMessageBox.Critical, QMessageBox.Ok)

    # Mover a la vista
    def show_error(self, title, text, info, icon, buttons):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setInformativeText(info)
        msg.setWindowTitle(title)
        msg.setStandardButtons(buttons)
        return msg.exec_()

    def remove_digital_pin(self, pin):
        if pin in self.__setup.digital_input_pins:
            self.__setup.digital_input_pins.remove(pin)

        if pin in self.__setup.digital_output_pins:
            self.__setup.digital_output_pins.remove(int(pin))

        if pin in self.__setup.pwm_pins:
            self.__setup.pwm_pins.remove(int(pin))

    def insert_analog_pin(self, pin_index, pin, type_idx):
        if pin_index < 0:
            return
        current = self.__main_window.get_current_board()["ANALOG_PINS"]
        target_pin = self.__setup.analog_input_pins if type_idx == 0 else self.__setup.analog_output_pins

        if pin in current and pin not in self.__setup.analog_input_pins and pin not in self.__setup.analog_output_pins:
            target_pin.append(pin)
            self.__main_window.addAnalogPin(pin_index, type_idx)
        else:
            self.show_error(
                "Error", "Assign error", "Could not set pin %d with the selected type" % (pin),
                QMessageBox.Critical, QMessageBox.Ok)

    def remove_analog_pin(self, pin):
        if pin in self.__setup.analog_input_pins:
            self.__setup.analog_input_pins.remove(pin)

        if pin in self.__setup.analog_output_pins:
            self.__setup.analog_output_pins.remove(pin)

    def check_connection(self):
        self.__connection_status = self.__main_window.create_connection_dialog()
        conn = self.start_connection()
        conn_checker = threading.Thread(target=self.conn_check, args=[conn])
        conn_checker.start()
        self.__connection_status.exec_()
        conn.wake_up()
        conn_checker.join()

    def conn_check(self, conn):
        try:
            config = ProtocolConfig(conn)
            arduino_if = init_interface(config)
            version = arduino_if.get_version()
            self.__connection_status.set_ok()
        except ConnectionTimeoutException:
            self.__connection_status.set_error("Error: connection timeout")
        except ConnectionException:
            self.__connection_status.set_error("Error: Board unreachable")
        except ValueError, err:
            self.__connection_status.set_error("Error: {0}".format(err))

    def board_changed(self, new_idx, old_idx):
        ret = QMessageBox.Yes

        if self.__setup.digital_input_pins or self.__setup.digital_output_pins or \
           self.__setup.analog_input_pins or self.__setup.analog_output_pins or self.__setup.pwm_pins:
            ret = self.show_error(
                "Warning", "Configuration reset", "Changing the board will reset all I/O pins configuration! Continue?",
                QMessageBox.Critical, QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            del self.__setup.digital_input_pins[:]
            del self.__setup.digital_output_pins[:]
            del self.__setup.analog_input_pins[:]
            del self.__setup.analog_output_pins[:]
            del self.__setup.pwm_pins[:]
            self.__setup = self.__setup._replace(board_type=boards.types[new_idx],
                                                 analog_resolution=boards.types[new_idx]["ANALOG_DEFAULT_RESOLUTION"])
            self.__main_window.set_board(new_idx)
            self.__main_window.update(self.__setup)
            return new_idx
        else:
            self.__main_window.set_board(old_idx)
            return old_idx

    def start_bench(self):
        try:
            self.__setup = self.__setup._replace(connection=self.start_connection(),
                                                 **self.__main_window.checkout_board_setup())
        except SerialConnectionException:
            self.show_error(
                "Error", "Connection failure", "Could not start connection to board",
                QMessageBox.Critical, QMessageBox.Ok)
            return

        bench = ArduinoBench()
        stats = ArduinoStatsDialog(bench)
        stats.connect_to_reset(bench)
        bench.add_observer(stats)
        bench.start(self.__setup)
        stats.exec_()
        bench.stop()

    def autodetect_board(self):
        board_id = boards.detect_board()

        if board_id and board_id != self.__main_window.current_board_idx():
            self.board_changed(board_id, self.__main_window.current_board_idx())

        return board_id

    def update_analog_resolution(self, value):
        self.__setup = self.__setup._replace(analog_resolution=value)


class EventScheduler:

    def __init__(self):
        self.stopped = False
        self.queue = []
        self.tasks_presents = threading.Condition()

    def start(self):
        self.thread = threading.Thread(target=self.svc)
        self.thread.start()

    def svc(self):
        while not self.stopped:
            with self.tasks_presents:
                if not self.queue and not self.stopped:
                    self.tasks_presents.wait()
                else:
                    for i in self.queue:
                        i()
                    del self.queue[:]

    def push_task(self, task):
        with self.tasks_presents:
            self.queue.append(task)
            self.tasks_presents.notify()

    def stop(self):
        with self.tasks_presents:
            self.stopped = True
            self.tasks_presents.notify()
        self.thread.join()
