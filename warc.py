# -*- coding: UTF-8 -*-

import os
from tempfile import NamedTemporaryFile
import shutil
from datetime import datetime

from hanzo.warctools import warc, WarcRecord
from hanzo.httptools import ResponseMessage

CONFORMS_TO = "http://bibnum.bnf.fr/WARC/WARC_ISO_28500_version1_latestdraft.pdf"

class Warc(object):
    _file_name = None
    _warc_file_read = None
    _warc_file_write = None
    _temporary = None
    _read_only = False

    def __init__(self, file_name, temporary=False, read_only=False):
        self._file_name = file_name
        self._temporary = temporary
        self._read_only = read_only if not self._temporary else False

        if self._temporary:
            self._warc_file_read = NamedTemporaryFile("rb")
            self._warc_file_write = open(self._warc_file_read.name, "wb")

            self._init_file()

        else:
            if self._read_only:
                self._warc_file_read = open(file_name, "rb")

            else:
                self._warc_file_read = open(file_name, "rb")
                self._warc_file_write = open(file_name, "ab")

    def find_record(self, url):
        self._warc_file_read.seek(0)
        wrs = WarcRecord.open_archive(file_handle=self._warc_file_read, \
                gzip="record")

        for (offset, record, errors) in wrs.read_records(limit=None):
            if record and (record.type == WarcRecord.RESPONSE) \
                    and (record.content[0] == ResponseMessage.CONTENT_TYPE) \
                    and (record.url == url):
                return record

        return None

    def write_record(self, record):
        if self._read_only:
            raise RuntimeError("WARC opened for read-only access")

        self._warc_file_write.seek(0, os.SEEK_END)
        record.write_to(self._warc_file_write, gzip=True)
        self._warc_file_write.flush()

    def make_permanent(self):
        if not self._temporary:
            raise RuntimeError("This WARC is not temporary")

        warc_file = open(self._file_name, "wb")
        self._warc_file_read.seek(0)

        # copy temp file to it's permanent location
        shutil.copyfileobj(self._warc_file_read, warc_file)

        self._warc_file_read = open(self._file_name, "rb")
        self._warc_file_write = warc_file

        self._temporary = False

    @property
    def temporary(self):
        return self._temporary

    @property
    def read_only(self):
        return self._read_only

    def _init_file(self):
        warcinfo_headers = [
            (WarcRecord.TYPE, WarcRecord.WARCINFO),
            (WarcRecord.ID, WarcRecord.random_warc_uuid()),
            (WarcRecord.DATE, warc.warc_datetime_str(datetime.utcnow())),
            (WarcRecord.FILENAME, os.path.basename(self._file_name)),
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

        self.write_record(warcinfo_record)
