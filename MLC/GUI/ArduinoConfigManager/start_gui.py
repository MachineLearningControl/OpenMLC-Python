import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from board_config_design import Ui_BoardConfigurationFrame
from pinout_design import Ui_BoardPinout
from pinout_dialog import ArduinoBoardDialog
from board_config_window import BoardConfigWindow

def showPinout():
   dialog = ArduinoBoardDialog("images/uno.jpg")
   dialog.exec_() 
#   window = QDialog()
#   ui = Ui_BoardPinout()
#   ui.setupUi(window)
#   window.exec_()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = BoardConfigWindow()
   #ui = Ui_BoardConfigurationFrame()
   #ui.setupUi(window)
   #ui.showPinout.clicked.connect(showPinout)
   
   window.show()
   sys.exit(app.exec_())




