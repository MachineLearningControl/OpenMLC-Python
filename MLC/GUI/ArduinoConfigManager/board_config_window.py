import sys

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5 import QtCore

from board_config_design import Ui_BoardConfigurationFrame
from pinout_dialog import ArduinoBoardDialog
from connection_dialog import ArduinoConnectionDialog

class BoardConfigWindow(QMainWindow):
   def __init__(self, parent=None):
      super(BoardConfigWindow, self).__init__(parent)
      self.ui = Ui_BoardConfigurationFrame()
      self.ui.setupUi(self)
      self.ui.showPinout.clicked.connect(self.showPinout)
      self.ui.arduinoBoard.clear()
      _translate = QtCore.QCoreApplication.translate
      self.setWindowTitle(_translate("BoardConfigurationFrame", "Board Configuration"))
      self.ui.arduinoBoard.insertItem(0, _translate("BoardConfigurationFrame", "Arduino Due"), QtCore.QVariant("images/due.png"))
      self.ui.arduinoBoard.insertItem(1, _translate("BoardConfigurationFrame", "Arduino Uno"), QtCore.QVariant("images/uno.jpg"))
      self.ui.arduinoBoard.insertItem(2, _translate("BoardConfigurationFrame", "Arduino Mega"), QtCore.QVariant("images/mega.png"))
      self.ui.addDigitalPin.clicked.connect(self.insertDigitalPin)
      self.ui.addPin.clicked.connect(self.insertAnalogPin)
      self.ui.testInterface.clicked.connect(self.checkConnection)

   def showPinout(self):
      index = self.ui.arduinoBoard.currentIndex()
      path = self.ui.arduinoBoard.itemData(index)
      dialog = ArduinoBoardDialog(path)
      dialog.exec_()

   def checkConnection(self):
      dialog = ArduinoConnectionDialog()
      dialog.exec_()

   def insertDigitalPin(self):
      self.insertPin(self.ui.digitalPins, self.ui.digitalPinType, self.ui.digitalPinsList)

   def insertAnalogPin(self):
      self.insertPin(self.ui.analogPins, self.ui.analogPinType,self.ui.analogPinList)

   def insertPin(self, pins, pinType, pinsList):
      pin=pins.currentIndex()
      t_pin = pins.currentText()
      p_type=pinType.currentText()
      row = pinsList.rowCount()
      if pin < 0:
         return
      pinsList.insertRow(row)
      widget=QTableWidgetItem(t_pin)
      widget.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
      pinsList.setItem(row, 0, widget)
      widget=QTableWidgetItem(p_type)
      widget.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
      pinsList.setItem(row, 1, widget)
      pinsList.verticalHeader().setVisible(False)
      pins.removeItem(pin)
      
