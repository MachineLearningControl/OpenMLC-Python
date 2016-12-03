from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(749, 585)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.projects_box = QtWidgets.QGroupBox(self.centralWidget)
        self.projects_box.setObjectName("projects_box")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.projects_box)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.projects_box)
        self.frame.setMinimumSize(QtCore.QSize(0, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.new_button = QtWidgets.QToolButton(self.frame)
        self.new_button.setObjectName("new_button")
        self.horizontalLayout_3.addWidget(self.new_button)
        self.clone_button = QtWidgets.QToolButton(self.frame)
        self.clone_button.setObjectName("clone_button")
        self.horizontalLayout_3.addWidget(self.clone_button)
        self.remove_button = QtWidgets.QToolButton(self.frame)
        self.remove_button.setObjectName("remove_button")
        self.horizontalLayout_3.addWidget(self.remove_button)
        self.verticalLayout.addWidget(self.frame, 0, QtCore.Qt.AlignLeft)
        self.listView = QtWidgets.QListView(self.projects_box)
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)
        self.horizontalLayout.addWidget(self.projects_box)
        self.description_box = QtWidgets.QGroupBox(self.centralWidget)
        self.description_box.setObjectName("description_box")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.description_box)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.description_list = QtWidgets.QListView(self.description_box)
        self.description_list.setObjectName("description_list")
        self.horizontalLayout_2.addWidget(self.description_list)
        self.horizontalLayout.addWidget(self.description_box)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 749, 19))
        self.menuBar.setObjectName("menuBar")
        self.menuMLC = QtWidgets.QMenu(self.menuBar)
        self.menuMLC.setObjectName("menuMLC")
        self.menuProperties = QtWidgets.QMenu(self.menuBar)
        self.menuProperties.setObjectName("menuProperties")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menu_properties = QtWidgets.QAction(MainWindow)
        self.menu_properties.setObjectName("menu_properties")
        self.menu_close = QtWidgets.QAction(MainWindow)
        self.menu_close.setObjectName("menu_close")
        self.menu_about = QtWidgets.QAction(MainWindow)
        self.menu_about.setObjectName("menu_about")
        self.menuMLC.addAction(self.menu_properties)
        self.menuMLC.addSeparator()
        self.menuMLC.addAction(self.menu_close)
        self.menuProperties.addAction(self.menu_about)
        self.menuBar.addAction(self.menuMLC.menuAction())
        self.menuBar.addAction(self.menuProperties.menuAction())

        self.retranslateUi(MainWindow)
        self.menu_close.triggered.connect(MainWindow.close)
        self.new_button.clicked.connect(MainWindow.on_new_button_clicked)
        self.menu_properties.triggered.connect(MainWindow.edit_gui_config)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MLC Project Manager"))
        self.projects_box.setTitle(_translate("MainWindow", "Projects"))
        self.new_button.setText(_translate("MainWindow", "New"))
        self.clone_button.setText(_translate("MainWindow", "Clone"))
        self.remove_button.setText(_translate("MainWindow", "Remove"))
        self.description_box.setTitle(_translate("MainWindow", "Description"))
        self.menuMLC.setTitle(_translate("MainWindow", "MLC"))
        self.menuProperties.setTitle(_translate("MainWindow", "Help"))
        self.menu_properties.setText(_translate("MainWindow", "Properties"))
        self.menu_properties.setToolTip(_translate("MainWindow", "Manager Properties"))
        self.menu_close.setText(_translate("MainWindow", "Close"))
        self.menu_close.setToolTip(_translate("MainWindow", "Close MLC Manager"))
        self.menu_about.setText(_translate("MainWindow", "About"))
        self.menu_about.setToolTip(_translate("MainWindow", "Project Information"))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../../../untitled/edit_properties.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Properties_Dialog(object):
    def setupUi(self, Properties_Dialog):
        Properties_Dialog.setObjectName("Properties_Dialog")
        Properties_Dialog.resize(400, 300)
        Properties_Dialog.setWindowFlags(Properties_Dialog.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)
        self.verticalLayout = QtWidgets.QVBoxLayout(Properties_Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtWidgets.QTableView(Properties_Dialog)
        self.tableView.setFrameShape(QtWidgets.QFrame.HLine)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(Properties_Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Properties_Dialog)
        self.buttonBox.accepted.connect(Properties_Dialog.accept)
        self.buttonBox.rejected.connect(Properties_Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Properties_Dialog)

    def retranslateUi(self, Properties_Dialog):
        _translate = QtCore.QCoreApplication.translate
        Properties_Dialog.setWindowTitle(_translate("Properties_Dialog", "MLC Manager Properties"))