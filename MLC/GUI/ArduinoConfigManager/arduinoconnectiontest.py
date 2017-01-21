# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'arduinoconnectiontest.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ArduinoConnectionTest(object):
    def setupUi(self, ArduinoConnectionTest):
        ArduinoConnectionTest.setObjectName("ArduinoConnectionTest")
        ArduinoConnectionTest.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ArduinoConnectionTest)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadingPanel = QtWidgets.QLabel(ArduinoConnectionTest)
        self.loadingPanel.setText("")
        self.loadingPanel.setAlignment(QtCore.Qt.AlignCenter)
        self.loadingPanel.setObjectName("loadingPanel")
        self.verticalLayout.addWidget(self.loadingPanel)
        self.label_2 = QtWidgets.QLabel(ArduinoConnectionTest)
        self.label_2.setMaximumSize(QtCore.QSize(2400, 25))
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(ArduinoConnectionTest)
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ArduinoConnectionTest)
        self.buttonBox.accepted.connect(ArduinoConnectionTest.accept)
        self.buttonBox.rejected.connect(ArduinoConnectionTest.reject)
        QtCore.QMetaObject.connectSlotsByName(ArduinoConnectionTest)

    def retranslateUi(self, ArduinoConnectionTest):
        _translate = QtCore.QCoreApplication.translate
        ArduinoConnectionTest.setWindowTitle(_translate("ArduinoConnectionTest", "Dialog"))
        self.label_2.setText(_translate("ArduinoConnectionTest", "<b>Checking connection...</b>"))

