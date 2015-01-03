# -*- coding: UTF-8 -*-

import os
import re
from tempfile import TemporaryFile
from datetime import datetime

# TODO: usar Qt5

from PyQt4.QtCore import QTimer, pyqtSignal, QObject, QSize, QUrl
from PyQt4.QtGui import QApplication, QImage, QPainter

from PyQt4.QtNetwork import QNetworkRequest, \
        QNetworkReply, \
        QNetworkAccessManager

from PyQt4.QtWebKit import QWebView

from billiard.process import Process

from celery import Celery, Task, registry

from hanzo.warctools import warc, WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
WARC_DIR = os.path.join(BASE_DIR, "warc")

celery = Celery("bardo.page_load", backend="amqp://", broker="amqp://")

# XXX: usar uma única instância de QApplication por worker?

def canonicalize_url(url):
    if re.match(r"^https?://[^/]+$", url):
        url += "/"

    return url

CONFORMS_TO = "http://bibnum.bnf.fr/WARC/WARC_ISO_28500_version1_latestdraft.pdf"

class WarcNetworkReply(QNetworkReply):
    _warc_record = None
    _temp_data = None
    _network_reply = None
    _data = None
    _offset = None

    def __init__(self, parent, warc_record=None, network_reply=None):
        super(WarcNetworkReply, self).__init__(parent)

        if ((warc_record is not None) and (network_reply is not None)) \
                or ((warc_record is None) and (network_reply is None)):
            raise RuntimeError("Especifique warc_record OU network_reply")

        self._offset = 0

        if warc_record is not None:
            self._init_from_warc_record(warc_record)

            self.setFinished(True)
            QTimer.singleShot(0, self.finished.emit)

        else:
            self._init_from_network_reply(network_reply)

    def _init_from_network_reply(self, network_reply):
        self._temp_data = TemporaryFile()

        self._network_reply = network_reply
        self._network_reply.readyRead.connect(self._reply_ready_read)
        self._network_reply.finished.connect(self._reply_finished)
        self._network_reply.error.connect(self._reply_error)

    def _init_from_warc_record(self, warc_record):
        self._warc_record = warc_record

        self.open(QNetworkReply.ReadOnly | QNetworkReply.Unbuffered)

        self.setUrl(QUrl(self._warc_record.url))

        rs = ResponseMessage(RequestMessage())
        rs.feed(self._warc_record.content[1])

        for name, value in rs.header.headers:
            self.setRawHeader(name, value)

        # TODO: obter esses dados do warc record
        self.setAttribute(QNetworkRequest.HttpStatusCodeAttribute, 200)
        self.setAttribute(QNetworkRequest.HttpReasonPhraseAttribute, "OK")

        QTimer.singleShot(0, self.metaDataChanged.emit)

        self._data = rs.get_body()

        QTimer.singleShot(0, self.readyRead.emit)

    def _reply_ready_read(self):
        self._temp_data.write(self._network_reply.readAll())

    def _reply_finished(self):
        self._network_reply.readyRead.disconnect(self._reply_ready_read)
        self._network_reply.finished.disconnect(self._reply_finished)
        self._network_reply.error.disconnect(self._reply_error)

        headers = dict()

        for header in self._network_reply.rawHeaderList():
            temp = str(self._network_reply.rawHeader(header))
            headers[str(header)] = re.sub("\s", " ", temp)

        # XXX: alguns cabeçalhos não farão sentido no WARC

        elements = []

        for name, value in headers.iteritems():
            elements.append(name + ": " + value)

        elements.append("")

        url = str(self._network_reply.url().toString())

        status_code = self._network_reply.attribute(QNetworkRequest \
                .HttpStatusCodeAttribute)

        assert(status_code.isValid())

        status_msg = self._network_reply.attribute(QNetworkRequest \
                .HttpReasonPhraseAttribute)

        assert(status_msg.isValid())

        self._temp_data.seek(0)

        h_status = "HTTP/1.1 " + str(status_code.toString()) + " " \
                + str(status_msg.toString())

        content_data = h_status + "\r\n" \
                + "\r\n".join(elements) + "\r\n" \
                + self._temp_data.read()

        content_type = ResponseMessage.CONTENT_TYPE

        content = (content_type, content_data)

        wr = warc.make_response(WarcRecord.random_warc_uuid(), 
                warc.warc_datetime_str(datetime.utcnow()), url, content, None)

        self._temp_data.close()
        self._temp_data = None

        self.manager()._write_warc_record(wr)

        self._init_from_warc_record(wr)

    def _reply_error(self):
        print "ERR"

        print self._network_reply.url().toString()

        print self._network_reply.error()

        self._data = ""

        if not self.isFinished():
            self.setFinished(True)
            QTimer.singleShot(0, self.finished.emit)

    def abort(self):
        print "AB", self.url()

        if not self.isFinished():
            self.setFinished(True)
            QTimer.singleShot(0, self.finished.emit)

        else:
            print "NAB"

    def isSequential(self):
        return True

    def bytesAvailable(self):
        ba = len(self._data) - self._offset \
                        + super(QNetworkReply, self).bytesAvailable()

        print "BA", self.url(), ba

        if (ba == 0) and not self.isFinished():
            print "FIN", self.url()

            self.setFinished(True)
            QTimer.singleShot(0, self.finished.emit)

        return ba

    def readData(self, max_size):
        max_size = min(max_size, len(self._data) - self._offset)
        start = self._offset
        self._offset += max_size

        print "RD", self.url(), max_size

        if len(self._data) - self._offset == 0:
            if not self.isFinished():
                print "FIN", self.url()

                self.setFinished(True)
                QTimer.singleShot(0, self.finished.emit)

        return str(self._data[start:self._offset])

    # TODO:
    #
    # aguardar headers para checar se CT permite cache
    #
    # processar HTML para reconstruir URLs apontando para cache
    #
    # implementar todos os sinais necessários

class WarcNetworkAccessManager(QNetworkAccessManager):
    timeout = pyqtSignal()

    _pending = 0
    _req_timer = None

    # XXX: acho que __init__ tem mais parâmetros
    def __init__(self):
        super(WarcNetworkAccessManager, self).__init__()

        self.finished.connect(self._finished)

    def createRequest(self, operation, request, data):
        url = request.url()

        print "-->", url

        warc_record = self._find_warc_record(canonicalize_url(url.toString()))

        if warc_record:
            network_reply = WarcNetworkReply(self, warc_record=warc_record)

        else:
            initial_reply = super(WarcNetworkAccessManager, self) \
                    .createRequest(operation, request, data)

            network_reply = WarcNetworkReply(self, network_reply=initial_reply)

        network_reply.setRequest(request)
        network_reply.setOperation(operation)

        self._pending += 1

        print ">>>", self._pending

        if self._req_timer is not None:
            self._req_timer.stop()
            self._req_timer = None

        return network_reply

    def _finished(self, reply):
        self._pending -= 1

        print "<<<", self._pending

        # vamos aguardar algum tempo para alguma outra requisição
        if self._pending == 0:
            self._req_timer = QTimer()
            self._req_timer.setInterval(2000)
            self._req_timer.setSingleShot(True)
            self._req_timer.timeout.connect(self.timeout)
            self._req_timer.start()

    def _req_timeout(self):
        self._req_timer = None
        QTimer.singleShot(0, self.timeout.emit)

    def _write_warc_record(self, warc_record):
        fn = os.path.join(WARC_DIR, self._get_warc_name(warc_record.url))

        if os.path.exists(fn):
            fh = open(fn, "ab+")

        else:
            fh = self._init_warc_file(fn)

        warc_record.write_to(fh, gzip=True)

    def _find_warc_record(self, url):
        fn = os.path.join(WARC_DIR, self._get_warc_name(url))

        try:
            wrs = WarcRecord.open_archive(fn)

        except IOError:
            return None

        for (offset, record, errors) in wrs.read_records(limit=None):
            if record and (record.type == WarcRecord.RESPONSE) \
                    and (record.content[0] == ResponseMessage.CONTENT_TYPE) \
                    and (record.url == url):
                print "== ENCONTRADO =="

                return record

        print "== NÃO ENCONTRADO =="

        return None

    def _get_warc_name(self, url):
        return "page-loader.warc.gz"

    def _init_warc_file(self, file_name):
        warcinfo_headers = [
            (WarcRecord.TYPE, WarcRecord.WARCINFO),
            (WarcRecord.ID, WarcRecord.random_warc_uuid()),
            (WarcRecord.DATE, warc.warc_datetime_str(datetime.utcnow())),
            (WarcRecord.FILENAME, os.path.basename(file_name)),
        ]

        warcinfo_fields = "\r\n".join([
            "software: bardo.pageloader",
            "format: WARC File Format 1.0",
            "conformsTo: " + CONFORMS_TO,
            "robots: unknown",
        ])

        warcinfo_content = ("application/warc-fields", warcinfo_fields)

        warcinfo_record = WarcRecord(headers=warcinfo_headers, \
                content=warcinfo_content)

        fh = open(file_name, "wb+")

        warcinfo_record.write_to(fh, gzip=True)

        return fh

class PageLoader(QObject):
    _app = None
    _custom_mgr = None
    _page = None
    _timer = None

    def load(self, url):
        self._app = QApplication([])
        self._page = QWebView()

        self._page.page().setViewportSize(QSize(1366, 768))
        self._custom_mgr = WarcNetworkAccessManager()
        self._page.page().setNetworkAccessManager(self._custom_mgr)
        self._custom_mgr.timeout.connect(self._timeout)
        self._page.load(QUrl(url))

        # tempo máximo de espera
        self._timer = QTimer()
        self._timer.setInterval(20000)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._timeout)
        self._timer.timeout.connect(self._timeout_geral)
        self._timer.start()

        self._app.exec_()

        return True

    def _timeout(self):
        print "TIMEOUT"

        self._timer.timeout.disconnect(self._timeout)
        self._custom_mgr.timeout.disconnect(self._timeout)

        image = QImage(self._page.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self._page.page().mainFrame().render(painter)
        painter.end()
        image.save("output.png")

        self._app.quit()

    def _timeout_geral(self):
        print "TIMEOUT GERAL"

@celery.task
class PageLoaderTask(Task):
    _page_loader = None

    def __init__(self):
        self._page_loader = PageLoader()

    def run(self, url):
        p = Process(target=self._run, args=[url])
        p.start()
        p.join()

    def _run(self, url):
        self._page_loader.load(url)

load_page = registry.tasks[PageLoaderTask.name]

if __name__ == "__main__":
    pl = PageLoader()

    pl.load("http://www.terra.com.br/")
