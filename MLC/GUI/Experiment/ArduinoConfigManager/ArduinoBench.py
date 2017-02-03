import random
import numpy
import time

from threading import Thread

class ArduinoBench:
   def __init__(self):
      self.__data = {"X":[], "Y":[]}
      self._observers = []
      self._run = False
      self._thread = None

   def add_observer(self, observer):
      self._observers.append(observer)
       
   def get_points(self):
      return self.__data 

   def evaluate(self, board_config):
      connection = SerialConnection(port=board_config["TERMINAL"])
      arduinoDue = ArduinoInterface(connection, board_config["BOARD"])

      arduinoDue.reset() #Just in case
      arduinoDue.set_report_mode("AVERAGE", read_count=2, read_delay=0)

      arduinoDue.add_output(40)
      arduinoDue.add_output(66)
      arduinoDue.add_input(54)

      last_time = time.time()
      start_time = last_time
      read_c = 0

      while self._run:
          output = arduinoDue.actuate([(40,1),(66,255)])
          read_c = read_c + 1
          new_time = time.time()

          if (new_time - start_time) > 1:
             read_c = 1
             start_time = new_time

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
      self.__data["X"]=[]
      self.__data["Y"]=[] 

   def _runner(self):
      while(self.__run):
         self.evaluate()

   def start(self):
      self._run = True
      self._thread = Thread(target=self._runner)
      self._thread.start() 

   def stop(self):
      self._run=False
      self._thread.join()

class MockArduinoBench(ArduinoBench):
   def __init__(self):
      ArduinoBench.__init__(self)

   def evaluate(self):
      self.get_points()["X"].append(len(self.get_points()["X"]))
      self.get_points()["Y"].append(random.randint(95,150))

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

      
      
