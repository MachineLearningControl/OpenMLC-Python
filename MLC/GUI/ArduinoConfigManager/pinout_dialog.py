from PyQt5.QtWidgets import QDialog
from pinout_design import Ui_BoardPinout

class ArduinoBoardDialog(QDialog):
   def __init__(self, board_path, parent=None):
      super(ArduinoBoardDialog, self).__init__(parent)
      self.ui = Ui_BoardPinout()
      self.ui.setupUi(self)
      self.ui.boardImage.setStyleSheet("image: url("+board_path+");")
      self.resize(650,650)
      
      
