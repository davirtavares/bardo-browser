# -*- coding: UTF-8 -*-

import os
import re
from tempfile import TemporaryFile
from datetime import datetime

# TODO: usar Qt5

# TODO: logging

# TODO: redirecionamentos

from PyQt4.QtCore import QTimer, QUrl, QString

from PyQt4.QtNetwork import QNetworkRequest, \
        QNetworkReply, \
        QNetworkAccessManager

from hanzo.warctools import warc, WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WARC_DIR = os.path.join(BASE_DIR, "warc")

def canonicalize_url(url):
    if re.match(r"^https?://[^/]+$", url):
        url += "/"

    return url

def qstring_to_str(qs):
    return unicode(qs.toUtf8(), encoding="utf-8").encode("utf-8")

def str_to_qstring(s):
    return QString.fromUtf8(s)

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

        else:
            self._init_from_network_reply(network_reply)

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

        QTimer.singleShot(0, self.metaDataChanged.emit)

        self._data = rs.get_body()

        QTimer.singleShot(0, self.readyRead.emit)
        QTimer.singleShot(0, self.finished.emit)

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

            QTimer.singleShot(0, self.finished.emit)

            return

        headers = dict()

        for header in self._network_reply.rawHeaderList():
            temp = str(self._network_reply.rawHeader(header))
            headers[str(header)] = re.sub("\s", " ", temp)

        # XXX: alguns cabeçalhos não farão sentido no WARC

        elements = []

        for name, value in headers.iteritems():
            elements.append(name + ": " + value)

        elements.append("")

        url = qstring_to_str(self._network_reply.url().toString())

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

        self._network_reply = None

    def _reply_error(self, code):
        self.error.emit(self._network_reply.error())

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

    # TODO:
    #
    # aguardar headers para checar se CT permite cache
    #
    # processar HTML para reconstruir URLs apontando para cache

class WarcNetworkAccessManager(QNetworkAccessManager):
    def createRequest(self, operation, request, data):
        url = qstring_to_str(request.url().toString())
        warc_record = self._find_warc_record(canonicalize_url(url))

        if warc_record:
            network_reply = WarcNetworkReply(self, warc_record=warc_record)

        else:
            initial_reply = super(WarcNetworkAccessManager, self) \
                    .createRequest(operation, request, data)

            network_reply = WarcNetworkReply(self, network_reply=initial_reply)

        network_reply.setRequest(request)
        network_reply.setOperation(operation)

        return network_reply

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

                return record

        return None

    def _get_warc_name(self, url):
        return "bardo-browser.warc.gz"

    def _init_warc_file(self, file_name):
        warcinfo_headers = [
            (WarcRecord.TYPE, WarcRecord.WARCINFO),
            (WarcRecord.ID, WarcRecord.random_warc_uuid()),
            (WarcRecord.DATE, warc.warc_datetime_str(datetime.utcnow())),
            (WarcRecord.FILENAME, os.path.basename(file_name)),
        ]

        warcinfo_fields = "\r\n".join([
            "software: bardo",
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
