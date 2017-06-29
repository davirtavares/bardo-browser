# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'browser.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Browser(object):
    def setupUi(self, Browser):
        Browser.setObjectName("Browser")
        Browser.resize(702, 607)
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        Browser.setFont(font)
        self.centralwidget = QtWidgets.QWidget(Browser)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_toolbar = QtWidgets.QVBoxLayout()
        self.main_toolbar.setObjectName("main_toolbar")
        self.url_toolbar = QtWidgets.QHBoxLayout()
        self.url_toolbar.setObjectName("url_toolbar")
        self.go_back = QtWidgets.QPushButton(self.centralwidget)
        self.go_back.setText("")
        icon = QtGui.QIcon.fromTheme("go-previous")
        self.go_back.setIcon(icon)
        self.go_back.setObjectName("go_back")
        self.url_toolbar.addWidget(self.go_back)
        self.go_forward = QtWidgets.QPushButton(self.centralwidget)
        self.go_forward.setAutoFillBackground(False)
        self.go_forward.setText("")
        icon = QtGui.QIcon.fromTheme("go-next")
        self.go_forward.setIcon(icon)
        self.go_forward.setObjectName("go_forward")
        self.url_toolbar.addWidget(self.go_forward)
        self.url_location = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.url_location.sizePolicy().hasHeightForWidth())
        self.url_location.setSizePolicy(sizePolicy)
        self.url_location.setObjectName("url_location")
        self.url_toolbar.addWidget(self.url_location)
        self.main_toolbar.addLayout(self.url_toolbar)
        self.toolbar = QtWidgets.QHBoxLayout()
        self.toolbar.setObjectName("toolbar")
        self.select_button = QtWidgets.QPushButton(self.centralwidget)
        self.select_button.setObjectName("select_button")
        self.toolbar.addWidget(self.select_button)
        self.save_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_button.setObjectName("save_button")
        self.toolbar.addWidget(self.save_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.toolbar.addItem(spacerItem)
        self.main_toolbar.addLayout(self.toolbar)
        self.verticalLayout_2.addLayout(self.main_toolbar)
        self.web_view = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.web_view.sizePolicy().hasHeightForWidth())
        self.web_view.setSizePolicy(sizePolicy)
        self.web_view.setObjectName("web_view")
        self.verticalLayout_2.addWidget(self.web_view)
        Browser.setCentralWidget(self.centralwidget)
        self.status_bar = QtWidgets.QStatusBar(Browser)
        self.status_bar.setObjectName("status_bar")
        Browser.setStatusBar(self.status_bar)

        self.retranslateUi(Browser)
        QtCore.QMetaObject.connectSlotsByName(Browser)

    def retranslateUi(self, Browser):
        _translate = QtCore.QCoreApplication.translate
        self.select_button.setText(_translate("Browser", "Select"))
        self.save_button.setText(_translate("Browser", "Save"))

from PyQt5 import QtWebEngineWidgets
