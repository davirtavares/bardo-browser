# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'browser.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Browser(object):
    def setupUi(self, Browser):
        Browser.setObjectName(_fromUtf8("Browser"))
        Browser.resize(702, 607)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        Browser.setFont(font)
        self.centralwidget = QtGui.QWidget(Browser)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.main_toolbar = QtGui.QVBoxLayout()
        self.main_toolbar.setSpacing(6)
        self.main_toolbar.setObjectName(_fromUtf8("main_toolbar"))
        self.url_toolbar = QtGui.QHBoxLayout()
        self.url_toolbar.setObjectName(_fromUtf8("url_toolbar"))
        self.go_back = QtGui.QPushButton(self.centralwidget)
        self.go_back.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-previous"))
        self.go_back.setIcon(icon)
        self.go_back.setObjectName(_fromUtf8("go_back"))
        self.url_toolbar.addWidget(self.go_back)
        self.go_forward = QtGui.QPushButton(self.centralwidget)
        self.go_forward.setAutoFillBackground(False)
        self.go_forward.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-next"))
        self.go_forward.setIcon(icon)
        self.go_forward.setObjectName(_fromUtf8("go_forward"))
        self.url_toolbar.addWidget(self.go_forward)
        self.url_location = QtGui.QLineEdit(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.url_location.sizePolicy().hasHeightForWidth())
        self.url_location.setSizePolicy(sizePolicy)
        self.url_location.setObjectName(_fromUtf8("url_location"))
        self.url_toolbar.addWidget(self.url_location)
        self.main_toolbar.addLayout(self.url_toolbar)
        self.toolbar = QtGui.QHBoxLayout()
        self.toolbar.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.toolbar.setObjectName(_fromUtf8("toolbar"))
        self.select_button = QtGui.QPushButton(self.centralwidget)
        self.select_button.setObjectName(_fromUtf8("select_button"))
        self.toolbar.addWidget(self.select_button)
        self.save_button = QtGui.QPushButton(self.centralwidget)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.toolbar.addWidget(self.save_button)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        self.toolbar.addItem(spacerItem)
        self.main_toolbar.addLayout(self.toolbar)
        self.main_toolbar.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.main_toolbar)
        self.main_frame = QtGui.QHBoxLayout()
        self.main_frame.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.main_frame.setObjectName(_fromUtf8("main_frame"))
        self.verticalLayout_2.addLayout(self.main_frame)
        self.verticalLayout_2.setStretch(1, 2)
        Browser.setCentralWidget(self.centralwidget)
        self.status_bar = QtGui.QStatusBar(Browser)
        self.status_bar.setObjectName(_fromUtf8("status_bar"))
        Browser.setStatusBar(self.status_bar)

        self.retranslateUi(Browser)
        QtCore.QMetaObject.connectSlotsByName(Browser)

    def retranslateUi(self, Browser):
        self.select_button.setText(_translate("Browser", "Selecionar", None))
        self.save_button.setText(_translate("Browser", "Salvar", None))

