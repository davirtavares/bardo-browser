# -*- coding: UTF-8 -*-

import re
from tempfile import TemporaryFile
from datetime import datetime

# TODO: use Qt5

# TODO: logging

# TODO: protocol "data:"

from PyQt4.QtCore import QTimer, QUrl, QString, QLatin1String

from PyQt4.QtNetwork import QNetworkRequest, \
        QNetworkReply, \
        QNetworkAccessManager

from hanzo.warctools import warc, WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage

def qstring_to_str(qs):
    return unicode(qs.toUtf8(), encoding="utf-8").encode("utf-8")

def str_to_qstring(s):
    return QString.fromUtf8(s)

class ErrorNetworkReply(QNetworkReply):
    def __init__(self, request, error_string, error, parent=None):
        super(ErrorNetworkReply, self).__init__(parent)

        self.setUrl(request.url())
        self.setOpenMode(QIODevice.ReadOnly)
        self.setError(error, error_string)

        QTimer.singleShot(0, lambda: self.error.emit(error))
        QTimer.singleShot(0, lambda: self.finished.emit())

    def abort(self):
        pass

    def bytesAvailable(self):
        return 0

    def readData(self):
        return bytes()

class ContentNotFoundNetworkReply(ErrorNetworkReply):
    def __init__(self, request, error_string, parent=None):
        super(ContentNotFoundNetworkReply, self) \
                .__init__(request, error_string, \
                    QNetworkReply.ContentNotFoundError, parent)

class WarcNetworkReply(QNetworkReply):
    _warc_record = None
    _temp_data = None
    _network_reply = None
    _data = None
    _offset = None

    def __init__(self, warc_record=None, network_reply=None, parent=None):
        super(WarcNetworkReply, self).__init__(parent)

        if ((warc_record is not None) and (network_reply is not None)) \
                or ((warc_record is None) and (network_reply is None)):
            raise RuntimeError("Specify warc_record OR network_reply")

        self._offset = 0

        if warc_record is not None:
            self._init_from_warc_record(warc_record)

        else:
            self._init_from_network_reply(network_reply)

    def abort(self):
        if self._network_reply:
            self._network_reply.readyRead.disconnect(self._reply_ready_read)
            self._network_reply.finished.disconnect(self._reply_finished)
            self._network_reply.error.disconnect(self._reply_error)
            self._network_reply.abort()
            self._network_reply = None

    def isSequential(self):
        return True

    def bytesAvailable(self):
        ba = len(self._data) - self._offset \
                + super(QNetworkReply, self).bytesAvailable()

        return ba

    def readData(self, max_size):
        max_size = min(max_size, len(self._data) - self._offset)
        start = self._offset
        self._offset += max_size

        return str(self._data[start:self._offset])

    def _init_from_network_reply(self, network_reply):
        self._data = ""

        self._temp_data = TemporaryFile()

        self._network_reply = network_reply
        self._network_reply.readyRead.connect(self._reply_ready_read)
        self._network_reply.finished.connect(self._reply_finished)
        self._network_reply.error.connect(self._reply_error)

    def _init_from_warc_record(self, warc_record):
        self._warc_record = warc_record
        self.open(QNetworkReply.ReadOnly | QNetworkReply.Unbuffered)
        self.setUrl(QUrl(str_to_qstring(self._warc_record.url)))

        rs = ResponseMessage(RequestMessage())
        rs.feed(self._warc_record.content[1])

        for name, value in rs.header.headers:
            self.setRawHeader(name, value)

        self.setAttribute(QNetworkRequest.HttpStatusCodeAttribute, \
                rs.header.code)
        self.setAttribute(QNetworkRequest.HttpReasonPhraseAttribute, \
                rs.header.phrase)

        self._check_for_redirect(rs.header.code)

        QTimer.singleShot(0, lambda: self.metaDataChanged.emit())

        self._data = rs.get_body()

        QTimer.singleShot(0, lambda: self.readyRead.emit())
        QTimer.singleShot(0, lambda: self.finished.emit())

    def _reply_ready_read(self):
        self._temp_data.write(self._network_reply.readAll())

    def _reply_finished(self):
        self._network_reply.readyRead.disconnect(self._reply_ready_read)
        self._network_reply.finished.disconnect(self._reply_finished)
        self._network_reply.error.disconnect(self._reply_error)

        status_code = self._network_reply.attribute(QNetworkRequest \
                .HttpStatusCodeAttribute)

        if not status_code.isValid():
            self._temp_data.close()
            self._temp_data = None
            self._network_reply = None

            QTimer.singleShot(0, lambda: self.finished.emit())

            return

        headers = dict()

        for header in self._network_reply.rawHeaderList():
            temp = str(self._network_reply.rawHeader(header))
            headers[str(header)] = re.sub("\s", " ", temp)

        elements = []

        for name, value in headers.iteritems():
            elements.append(name + ": " + value)

        elements.append("")

        url = qstring_to_str(self._network_reply.url().toString())

        status_msg = self._network_reply.attribute(QNetworkRequest \
                .HttpReasonPhraseAttribute)

        assert(status_msg.isValid())

        self._temp_data.seek(0)

        # XXX: we can't get HTTP version from Qt, assumes 1.1
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

        self.manager().current_warc.write_record(wr)

        self._init_from_warc_record(wr)

        self._network_reply = None

    def _reply_error(self, code):
        self.error.emit(self._network_reply.error())

    def _check_for_redirect(self, status_code):
        if status_code in (301, 302, 303, 307):
            header = self.rawHeader("Location")
            url = QUrl.fromEncoded(header)

            if not url.isValid():
                url = QUrl(QLatin1String(header))

            self.setAttribute(QNetworkRequest.RedirectionTargetAttribute, url)

class WarcNetworkAccessManager(QNetworkAccessManager):
    _current_warc = None

    def createRequest(self, operation, request, data):
        if not self._current_warc:
            return super(WarcNetworkAccessManager, self) \
                    .createRequest(operation, request, data)

        url = qstring_to_str(request.url().toString())
        warc_record = self._current_warc.find_record(url)

        if warc_record:
            network_reply = WarcNetworkReply(warc_record=warc_record, \
                    parent=self)

        else:
            if not self._current_warc.read_only:
                initial_reply = super(WarcNetworkAccessManager, self) \
                        .createRequest(operation, request, data)

                network_reply = WarcNetworkReply(network_reply=initial_reply, \
                        parent=self)

            else:
                network_reply = ContentNotFoundNetworkReply(request, \
                        "Content not found on WARC file", self)

        network_reply.setRequest(request)
        network_reply.setOperation(operation)

        return network_reply

    @property
    def current_warc(self):
        return self._current_warc

    @current_warc.setter
    def current_warc(self, warc):
        self._current_warc = warc
