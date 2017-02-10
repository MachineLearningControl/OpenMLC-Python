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
