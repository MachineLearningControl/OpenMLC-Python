import random
import numpy
import time

from threading import Thread

from MLC.arduino.protocol import ProtocolConfig, BuildSerial


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
        arduino = BuildSerial(self._board_config)

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
