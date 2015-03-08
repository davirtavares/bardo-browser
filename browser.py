# -*- coding: UTF-8 -*-

import sys

from PyQt4.QtCore import Qt, QEvent
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtWebKit import QWebSettings

from warcnam import WarcNetworkAccessManager
from uibrowser import Ui_Browser

class WebElementHighlighter(QtGui.QWidget):
    selection_color = QtGui.QColor(255, 0, 0)
    highlight_color = QtGui.QColor(0, 0, 255)

    _elements = None
    _highlighted_elements = None

    def __init__(self, parent):
        super(WebElementHighlighter, self).__init__(parent)

        self._elements = []
        self._highlighted_elements = []
        self.initUI()

    def add_element(self, element):
        try:
            self._elements.remove(element)

        except ValueError:
            pass

        self._elements.append(element)
        self.update()

    def remove_element(self, element):
        try:
            self._elements.remove(element)

        except ValueError:
            pass

        self.update()

    def clear_elements(self):
        del self._elements[:]

        self.update()

    def highlight_element(self, element):
        self.highlight_elements([element])

    def highlight_elements(self, element_list):
        new_list = []

        if element_list:
            new_list = element_list

        if cmp(new_list, self._highlighted_elements) == 0:
            return

        self._highlighted_elements[:] = new_list
        self.update()

    def initUI(self):
        self.setMinimumSize(300, 300)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred, \
                QtGui.QSizePolicy.Preferred)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        selections = [
            (self.selection_color, self._get_element_rect(e))
            for e in self._elements
        ] + [
            (self.highlight_color, self._get_element_rect(e))
            for e in self._highlighted_elements
        ]

        for sel in selections:
            qp.setPen(sel[0])
            qp.drawRect(sel[1])

    def _get_element_rect(self, e):
        view_rect = e.webFrame().geometry()
        sgh = e.webFrame().scrollBarGeometry(Qt.Horizontal)
        sgv = e.webFrame().scrollBarGeometry(Qt.Vertical)
        view_rect.setWidth(view_rect.width() - sgv.width())
        view_rect.setHeight(view_rect.height() - sgh.height())

        rect = e.geometry()
        sp = e.webFrame().scrollPosition()
        rect.translate(-sp.x(), -sp.y())

        if rect.x() + rect.width() > view_rect.x() + view_rect.width():
            rect.setRight(view_rect.x() + view_rect.width())

        if rect.y() + rect.height() > view_rect.y() + view_rect.height():
            rect.setBottom(view_rect.y() + view_rect.height())

        return rect

class Browser(QtGui.QMainWindow):
    _ui = None
    _warc_nan = None
    _highlighter = None

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self._ui = Ui_Browser()
        self._warc_nan = WarcNetworkAccessManager()

        self._ui.setupUi(self)
        self._highlighter = WebElementHighlighter(self._ui.frame)

        self._ui.web_view.installEventFilter(self)
        self._ui.web_view.setMouseTracking(True)
        self._ui.web_view.page().setNetworkAccessManager(self._warc_nan)

        self.resize(500, 600)

        self._highlighter.resize(self.size())

        self.connect(self._ui.url_location, QtCore.SIGNAL("returnPressed()"), self.browse)
        self.connect(self._ui.go_back, QtCore.SIGNAL("clicked()"), self._ui.web_view.back)
        self.connect(self._ui.go_forward, QtCore.SIGNAL("clicked()"), self._ui.web_view.forward)
        self.connect(self._ui.web_view, QtCore.SIGNAL("urlChanged(const QUrl)"), self.url_changed)

        self.connect(self._ui.test_button, QtCore.SIGNAL("clicked()"), self.test)

        self.default_url = "http://g1.globo.com/economia/mercados/noticia/2015/02/dolar-fecha-em-forte-alta-e-passa-de-r-283-nesta-terca.html"
        self._ui.url_location.setText(self.default_url)
        self.browse()

    def browse(self):
        url = self._ui.url_location.text() \
                if self._ui.url_location.text() \
                else self.default_url

        self._ui.web_view.load(QtCore.QUrl(url))
        self._ui.web_view.show()

    def url_changed(self, url):
        self._ui.url_location.setText(url.toString())

    def resizeEvent(self, event):
        self._highlighter.resize(event.size())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            hit_test_result = self._ui.web_view.page().mainFrame() \
                    .hitTestContent(event.pos())

            if not hit_test_result.isNull():
                self.highlight_element(hit_test_result.enclosingBlockElement())

            else:
                self.highlight_element(None)

        return QtGui.QMainWindow.eventFilter(self, obj, event)

    def select_element(self):
        pass

    def highlight_element(self, element):
        self._highlighter.highlight_element(element)

    def test(self):
        h1 = self._ui.web_view.page().mainFrame().documentElement() \
                .findFirst("h1")

        self._highlighter.add_element(h1)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
    main = Browser()

    main.show()

    sys.exit(app.exec_())
