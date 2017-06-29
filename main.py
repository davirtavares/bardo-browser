import os
import sys
import json

import urltools

from PyQt5.QtCore import QObject, QFile, QIODevice, QJsonValue, QJsonParseError, pyqtSlot, pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineScript, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel, QWebChannelAbstractTransport
from PyQt5.QtWebSockets import QWebSocketServer
from PyQt5.QtNetwork import QHostAddress, QNetworkProxy

from browser import Ui_Browser
from warc import Warc
from proxy import WARCProxyServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WARC_DIR = os.path.join(BASE_DIR, "warc")

class QJsonValueJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QJsonValue):
            return obj.toVariant()

        else:
            return super().default(obj)

class APPHandler(QObject):
    @pyqtSlot()
    def test(self):
        print("call received")

class WebSocketTransport(QWebChannelAbstractTransport):
    _socket = None

    def __init__(self, socket):
        super().__init__(socket)

        self._socket = socket
        self._socket.textMessageReceived.connect(self.textMessageReceived)

    def sendMessage(self, message):
        self._socket.sendTextMessage(json.dumps(message, cls=QJsonValueJSONEncoder))

    @pyqtSlot(str)
    def textMessageReceived(self, messageData):
        self.messageReceived.emit(json.loads(messageData), self)

class WebSocketClientWrapper(QObject):
    _server = None

    clientConnected = pyqtSignal(QWebChannelAbstractTransport)

    def __init__(self, server, parent=None):
        super().__init__(parent)

        self._server = server
        self._server.newConnection.connect(self.handleNewConnection)

    @pyqtSlot()
    def handleNewConnection(self):
        self.clientConnected.emit(WebSocketTransport(self._server.nextPendingConnection()))

class WebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def certificateError(self, certificateError):
        return True if certificateError.isOverridable() else False

class Browser(QtWidgets.QMainWindow):
    _application = None
    _ui = None
    _channel = None
    _handler = None
    _server = None
    _client_wrapper = None
    _server_port = 0
    _proxy_server = None
    _main_page = None

    def __init__(self, application, parent=None):
        super().__init__(parent)

        self._application = application
        self._application.aboutToQuit.connect(self._about_to_quit)

        self._ui = Ui_Browser()
        self._ui.setupUi(self)

        self._channel = QWebChannel(self)
        self._handler = APPHandler(self._channel)
        self._channel.registerObject("app", self._handler)

        self._server = QWebSocketServer("", QWebSocketServer.NonSecureMode, self)
        self._client_wrapper = WebSocketClientWrapper(self._server, self._server)
        self._client_wrapper.clientConnected.connect(self._channel.connectTo)
        self._server.listen(QHostAddress.LocalHost)
        self._server_port = self._server.serverPort()

        self._main_page = WebEnginePage(self)
        self._ui.web_view.setPage(self._main_page)

        self._install_app_js()
        self._setup_proxy()

        self.resize(800, 600)

        self._ui.url_location.returnPressed.connect(self._browse)
        self._ui.go_back.clicked.connect(self._ui.web_view.back)
        self._ui.go_forward.clicked.connect(self._ui.web_view.forward)
        self._ui.web_view.urlChanged.connect(self._url_changed)
        self._ui.select_button.clicked.connect(self._select)
        self._ui.save_button.clicked.connect(self._save)

        self._ui.url_location.setText("https://badssl.com/")
        self._browse()

    @pyqtSlot()
    def _browse(self):
        url = self._ui.url_location.text() \
                if self._ui.url_location.text() \
                else self.default_url

        self._ui.web_view.page().load(QtCore.QUrl(url))

    @pyqtSlot("QUrl")
    def _url_changed(self, url):
        try:
            url_s = self._ui.web_view.url().toString()
           #self._warc_nam.current_warc = self._get_warc_for_url(url_s)

        finally:
            self._ui.url_location.setText(url.toString())

    @pyqtSlot(bool)
    def _select(self):
        pass

    @pyqtSlot(bool)
    def _save(self):
       #self._warc_nam.current_warc.make_permanent()
        pass

    @pyqtSlot()
    def _about_to_quit(self):
        self._proxy_server.stop()

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

    def _install_app_js(self):
        self._inject_js_file(":/qtwebchannel/qwebchannel.js")
        self._inject_js_template(os.path.join(BASE_DIR, "config.js.tpl"), \
                context={ "serverPort": self._server_port })
        self._inject_js_file(os.path.join(BASE_DIR, "app.js"), QWebEngineScript.DocumentReady)

    def _inject_js_file(self, path, injection_point=QWebEngineScript.DocumentCreation):
        js_file = QFile(path)
        js_file.open(QIODevice.ReadOnly)

        source = bytes(js_file.readAll()).decode("utf-8")

        self._inject_js(source, os.path.basename(path), injection_point)

    def _inject_js_template(self, path, injection_point=QWebEngineScript.DocumentCreation, context=None):
        js_file = QFile(path)
        js_file.open(QIODevice.ReadOnly)

        template = bytes(js_file.readAll()).decode("utf-8")
        source = template.format(**(context if context is not None else {}))

        name = os.path.basename(path).rsplit(".", 1)[0] # removes .tpl
        self._inject_js(source, name, injection_point)

    def _inject_js(self, source, name, injection_point=QWebEngineScript.DocumentCreation):
        js = QWebEngineScript()
        js.setName(name)

        js.setSourceCode(source)
        js.setWorldId(QWebEngineScript.ApplicationWorld)
        js.setInjectionPoint(injection_point)
        js.setRunsOnSubFrames(False)

        QWebEngineProfile.defaultProfile().scripts().insert(js)

    def _setup_proxy(self):
        self._proxy_server = WARCProxyServer()
        self._proxy_server.start()

        proxy_conf = QNetworkProxy()
        proxy_conf.setHostName("127.0.0.1")
        proxy_conf.setPort(self._proxy_server.port)
        proxy_conf.setType(QNetworkProxy.HttpProxy)

        QNetworkProxy.setApplicationProxy(proxy_conf)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main = Browser(app)
    main.show()

    sys.exit(app.exec_())
