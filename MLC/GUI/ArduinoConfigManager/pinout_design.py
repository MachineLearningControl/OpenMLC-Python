# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pinout_design.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BoardPinout(object):
    def setupUi(self, BoardPinout):
        BoardPinout.setObjectName("BoardPinout")
        BoardPinout.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(BoardPinout)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(BoardPinout)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.boardImage = QtWidgets.QWidget(BoardPinout)
        self.boardImage.setStyleSheet("image: url(:/boards/images/uno.jpg);")
        self.boardImage.setObjectName("boardImage")
        self.gridLayout.addWidget(self.boardImage, 0, 0, 1, 1)

        self.retranslateUi(BoardPinout)
        self.buttonBox.accepted.connect(BoardPinout.accept)
        self.buttonBox.rejected.connect(BoardPinout.reject)
        QtCore.QMetaObject.connectSlotsByName(BoardPinout)

    def retranslateUi(self, BoardPinout):
        _translate = QtCore.QCoreApplication.translate
        BoardPinout.setWindowTitle(_translate("BoardPinout", "Dialog"))

