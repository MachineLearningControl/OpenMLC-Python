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

import random
import numpy
import time

from threading import Thread

from MLC.arduino.protocol import ProtocolConfig, init_interface


class ArduinoBench:

    def __init__(self):
        self.__data = {"X": [], "Y": []}
        self._observers = []
        self._run = False
        self._thread = None

    def add_observer(self, observer):
        self._observers.append(observer)

    def get_points(self):
        return self.__data

    def evaluate(self):
        arduino = init_interface(self._board_config)

        last_time = time.time()
        start_time = last_time
        epoch = last_time
        read_c = 0

        actuate_input = []
        for pin in self._board_config.digital_output_pins + self._board_config.analog_output_pins:
            actuate_input.append((pin, 0))

        while self._run:
            output = arduino.actuate(actuate_input)
            read_c = read_c + 1
            new_time = time.time()

            if (new_time - start_time) > 1:
                self.get_points()["X"].append(new_time - epoch)
                self.get_points()["Y"].append(read_c)

                read_c = 1
                start_time = new_time
                for i in self._observers:
                    i.update()

            last_time = new_time

    def get_avg(self):
        return numpy.average(self.__data["Y"])

    def std_deviation(self):
        return numpy.std(self.__data["Y"])

    def get_max(self):
        return max(self.__data["Y"])

    def get_min(self):
        return min(self.__data["Y"])

    def reset(self):
        self.__data["X"] = []
        self.__data["Y"] = []

    def _runner(self):
        while(self._run):
            self.evaluate()

    def start(self, config):
        self._board_config = config
        self._run = True
        self._thread = Thread(target=self._runner)
        self._thread.start()

    def stop(self):
        self._run = False
        self._thread.join()


class MockArduinoBench(ArduinoBench):

    def __init__(self):
        ArduinoBench.__init__(self)

    def evaluate(self):
        self.get_points()["X"].append(len(self.get_points()["X"]))
        self.get_points()["Y"].append(random.randint(95, 150))

        for i in self._observers:
            i.update()

    def _runner(self):
        while(self._run):
            time.sleep(1)
            self.evaluate()

    def reset(self):
        if self._run:
            self.stop()
            ArduinoBench.reset(self)
            self.start()
        else:
            ArduinoBench.reset(self)
