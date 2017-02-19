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

import sys
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication
from ArduinoBoardDialog import ArduinoBoardDialog
from ArduinoStatsDialog import ArduinoStatsDialog
from threading import Thread
from ArduinoBench import MockArduinoBench
import time


class Foo(QObject):

    # Define a new signal called 'trigger' that has no arguments.
    trigger = pyqtSignal()

    def connect_and_emit_trigger(self, function):
        # Connect the trigger signal to a slot.
        self.trigger.connect(function)

    def handle_trigger(self):
        # Show that the slot has been called.

        print "trigger signal received"

    def emit(self):
        self.trigger.emit()


class Worker(Thread):

    def __init__(self, bench):
        Thread.__init__(self)
        self.__run = True
        self.__bench = bench

    def run(self):
        while(self.__run):
            time.sleep(1)
            self.__bench.evaluate()
            # self.__signal.emit()

    def stop(self):
        self.__run = False

    def get_bench(self):
        return self.__bench


if __name__ == '__main__':
    app = QApplication(sys.argv)
    bench = MockArduinoBench()
    stats = ArduinoStatsDialog(bench)
    bench.add_observer(stats)
    stats.connect_to_reset(bench)
    # worker = Worker(bench)
    # worker.start()
    bench.start()
    stats.exec_()
    bench.stop()
