from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QMovie
from PyQt5.QtGui import QPixmap
from arduinoconnectiontest import Ui_ArduinoConnectionTest

class ArduinoConnectionDialog(QDialog):
   def __init__(self, parent=None):
      super(ArduinoConnectionDialog, self).__init__(parent)
      self.ui = Ui_ArduinoConnectionTest()
      self.ui.setupUi(self)
      #self.ui.widget.setStyleSheet("image: url(images/connection.gif);")
      self.__ok_tick = QPixmap()
      self.__ok_tick.load("./images/ok_b.png")
      self.__ok_tick = self.__ok_tick.scaled(100,100)
      self.__error_tick = QPixmap()
      self.__error_tick.load("./images/error.png")
      self.__error_tickt = self.__error_tick.scaled(100,100)
      self.__movie = QMovie()
      self.__movie.setFileName("./images/connection.gif")
      #self.ui.loadingPanel.setMovie(self.movie)
      self.set_ok()
      self.__movie.start()
      self.resize(150,150)

   def set_ok(self):
      self.ui.loadingPanel.setPixmap(self.__ok_tick)


   def set_error(self):
      self.ui.loadingPanel.setPixmap(self.__error_tick)
      

      
