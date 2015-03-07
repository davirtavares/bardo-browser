# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'browser.ui'
#
# Created: Tue Feb 10 16:14:44 2015
#      by: PyQt4 UI code generator 4.11.3
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
        Browser.resize(721, 607)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        Browser.setFont(font)
        self.centralwidget = QtGui.QWidget(Browser)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.main_toolbar = QtGui.QVBoxLayout()
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
        self.toolbar.setObjectName(_fromUtf8("toolbar"))
        self.test_button = QtGui.QPushButton(self.centralwidget)
        self.test_button.setObjectName(_fromUtf8("test_button"))
        self.toolbar.addWidget(self.test_button)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.toolbar.addItem(spacerItem)
        self.main_toolbar.addLayout(self.toolbar)
        self.verticalLayout_2.addLayout(self.main_toolbar)
        self.frame = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.web_view = QtWebKit.QWebView(self.frame)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.web_view.setFont(font)
        self.web_view.setObjectName(_fromUtf8("web_view"))
        self.horizontalLayout_2.addWidget(self.web_view)
        self.verticalLayout_2.addWidget(self.frame)
        Browser.setCentralWidget(self.centralwidget)
        self.status_bar = QtGui.QStatusBar(Browser)
        self.status_bar.setObjectName(_fromUtf8("status_bar"))
        Browser.setStatusBar(self.status_bar)

        self.retranslateUi(Browser)
        QtCore.QMetaObject.connectSlotsByName(Browser)

    def retranslateUi(self, Browser):
        self.test_button.setText(_translate("Browser", "Teste", None))

from PyQt4 import QtWebKit
