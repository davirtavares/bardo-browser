# -*- coding: UTF-8 -*-

import os
import sys
import urltools

from PyQt4.QtCore import Qt, QEvent
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtWebKit import QWebSettings, QWebPage

from warcnam import WarcNetworkAccessManager, qstring_to_str
from uibrowser import Ui_Browser
from warc import Warc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WARC_DIR = os.path.join(BASE_DIR, "warc")

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
        del self._highlighted_elements[:]

        self.update()

    def highlight_element(self, element):
        self.highlight_elements([element] if element else [])

    def highlight_elements(self, element_list):
        new_list = []

        if element_list:
            new_list = element_list

        if cmp(new_list, self._highlighted_elements) == 0:
            return

        self._highlighted_elements = new_list[:]
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
    BROWSER_MODE_NORMAL = 1
    BROWSER_MODE_SELECTION = 2

    _browser_mode = None
    _ui = None
    _warc_nan = None
    _highlighter = None
    _selecting = False

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self._ui = Ui_Browser()
        self._ui.setupUi(self)
        self._highlighter = WebElementHighlighter(self._ui.frame)

        self._warc_nan = WarcNetworkAccessManager()
        self.switch_mode(self.BROWSER_MODE_NORMAL)

        self._ui.web_view.installEventFilter(self)
        self._ui.web_view.setMouseTracking(True)
        self._ui.web_view.page().setNetworkAccessManager(self._warc_nan)

        self.resize(800, 600)

        self._highlighter.resize(self.size())

        self.connect(self._ui.url_location, QtCore.SIGNAL("returnPressed()"), self.browse)
        self.connect(self._ui.go_back, QtCore.SIGNAL("clicked()"), self._ui.web_view.back)
        self.connect(self._ui.go_forward, QtCore.SIGNAL("clicked()"), self._ui.web_view.forward)
        self.connect(self._ui.web_view, QtCore.SIGNAL("urlChanged(const QUrl)"), self.url_changed)
        self.connect(self._ui.select_button, QtCore.SIGNAL("clicked()"), self.select)
        self.connect(self._ui.save_button, QtCore.SIGNAL("clicked()"), self.save)

        self.default_url = "http://g1.globo.com/economia/mercados/noticia/2015/02/dolar-fecha-em-forte-alta-e-passa-de-r-283-nesta-terca.html"

        self._ui.url_location.setText(self.default_url)
        self.browse()

    def resizeEvent(self, event):
        self._highlighter.resize(event.size())

    def eventFilter(self, obj, event):
        try:
            if (event.type() == QEvent.MouseMove) and self._selecting:
                self._handle_mouse_move(event.pos())

        finally:
            return QtGui.QMainWindow.eventFilter(self, obj, event)

    def browse(self):
        url = self._ui.url_location.text() \
                if self._ui.url_location.text() \
                else self.default_url

        self._highlighter.clear_elements()
        self._ui.web_view.load(QtCore.QUrl(url))
        self._ui.web_view.show()

    def url_changed(self, url):
        try:
            self.switch_mode(self.BROWSER_MODE_NORMAL)
            url_s = qstring_to_str(self._ui.web_view.url().toString())
            self._warc_nan.current_warc = self._get_warc_for_url(url_s)

        finally:
            self._ui.url_location.setText(url.toString())

    def switch_mode(self, new_mode):
        if (new_mode != self.BROWSER_MODE_NORMAL) \
                and (new_mode != self.BROWSER_MODE_SELECTION):
            raise ValueError("Invalid browser mode")

        if new_mode == self._browser_mode:
            return

        if new_mode == self.BROWSER_MODE_NORMAL:
            self._ui.select_button.setText("Selecionar")
            self._ui.save_button.setEnabled(False)

        else: # new_mode == self.BROWSER_MODE_SELECTION:
            self._ui.select_button.setText("Cancelar")
            self._ui.save_button.setEnabled(True)

        self.cancel_selection()
        self._browser_mode = new_mode

    def select_element(self):
        self._selecting = True

    def cancel_selection(self):
        self._selecting = False
        self.highlight_element(None)

    def highlight_element(self, element):
        self._highlighter.highlight_element(element)

    def select(self):
        if self._browser_mode != self.BROWSER_MODE_SELECTION:
            self.switch_mode(self.BROWSER_MODE_SELECTION)

        else:
            self.switch_mode(self.BROWSER_MODE_NORMAL)

    def save(self):
        if self._browser_mode != self.BROWSER_MODE_SELECTION:
            return

        self._warc_nan.current_warc.make_permanent()
        self.switch_mode(self.BROWSER_MODE_NORMAL)

    def _get_warc_for_url(self, url):
        warc = self._find_warc(url)

        if not warc:
            warc_file = os.path.join(WARC_DIR, "bardo-browser.warc.gz")
            warc = Warc(warc_file, temporary=True, main_url=url)

        return warc

    def _find_warc(self, url):
        return None

    def _compare_urls(self, url1, url2):
        return (self._normalize_url(url1) == self._normalize_url(url2))

    def _normalize_url(self, url):
        return urltools.normalize(url)

    def _handle_mouse_move(self, pos):
        hit_result = self._ui.web_view.page().mainFrame().hitTestContent(pos)

        if not hit_result.isNull():
            element = hit_result.enclosingBlockElement()

            if not element.isNull():
                self.highlight_element(element)

            else:
                self.highlight_element(None)

        else:
            self.highlight_element(None)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    QWebSettings.globalSettings() \
            .setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

    main = Browser()
    main.show()

    sys.exit(app.exec_())
