# -*- coding: UTF-8 -*-

import os
from cStringIO import StringIO
from urlparse import urlparse
from functools import partial
from datetime import datetime
import zlib
import bz2

from cefpython3 import cefpython as cef
import gevent
from grequests import Pool
import grequests
from hanzo.warctools import warc, WarcRecord
from hanzo.httptools import RequestMessage, ResponseMessage

from cefutil import strongref
from warc import Warc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WARC_DIR = os.path.join(BASE_DIR, "warc")

REQUEST_POOLSIZE = 20

DECOMPRESSOR = {
    "deflate": partial(zlib.decompressobj, -zlib.MAX_WBITS),
    "gzip": partial(zlib.decompressobj, 16 + zlib.MAX_WBITS),
    "bzip2": bz2.BZ2Decompressor,
}

@strongref
class WARCResourceHandler(object):
    _request_handler = None
    _warc_record = None
    _request = None
    _response = None
    _response_cb = None

    def __init__(self, request_handler, warc_record=None, request=None):
        if ((warc_record is not None) and (request is not None)) \
                or ((warc_record is None) and (request is None)):
            raise RuntimeError("You must specify either warc_record OR request")

        self._request_handler = request_handler

        if warc_record is not None:
            self._init_from_warc_record(warc_record)

        else:
            # gevent operations should occur at the main thread
            cef.PostTask(cef.TID_UI, self._init_from_request, request)

    def ProcessRequest(self, request, callback):
        self._response_cb = callback

        return True

    def GetResponseHeaders(self, response, response_length_out, redirect_url_out):
        response.SetStatus(self._response.status_code)
        response.SetStatusText(self._response.status_text)

        if "Content-Type" in self._response.headers:
            if "text/html" in self._response.headers["Content-Type"]:
                response.SetMimeType("text/html")

            else:
                response.SetMimeType(self._response.headers["Content-Type"])

        response.SetHeaderMap(self._response.headers)

        if "Content-Length" in self._response.headers:
            response_length_out[0] = int(self._response.headers["Content-Length"])

        else:
            response_length_out[0] = -1

        if self._response.is_redirect():
            redirect_url_out[0] = self._response.headers["Location"]

    def ReadResponse(self, data_out, bytes_to_read, bytes_read_out, callback):
        data = self._response.content.read(bytes_to_read)

        if data:
            data_out[0] = bytes(data)
            bytes_read_out[0] = len(data)

            return True

        else:
            return False

    def CanGetCookie(self, cookie):
        return True

    def CanSetCookie(self, cookie):
        return True

    def Cancel(self):
        # TODO
        pass

    def _response_ready(self, response, *args, **kwargs):
        # https://docs.python.org/2/library/httplib.html?highlight=version#httplib.HTTPResponse.version
        http_version = "HTTP/1.0" if response.raw.version == 10 else "HTTP/1.1"

        http_status = http_version + " " + str(response.status_code) + " " \
                + str(response.reason)

        headers = []

        for name, value in response.headers.items():
            headers.append(name + ": " + value)

        content_data = http_status + "\r\n" \
                + "\r\n".join(headers) + "\r\n" + "\r\n" \
                + response.raw.read()

        content = (ResponseMessage.CONTENT_TYPE, content_data)

        wr = warc.make_response(WarcRecord.random_warc_uuid(),
                warc.warc_datetime_str(datetime.utcnow()), response.url, content, None)

        self._request_handler.current_warc.write_record(wr)

        self._init_from_warc_record(wr)

    def _init_from_warc_record(self, warc_record):
        self._warc_record = warc_record

        rs = ResponseMessage(RequestMessage(), ignore_headers=("Content-Encoding", ))
        rs.feed(warc_record.content[1])

        self._response = WARCResponse(warc_record.url, rs.header.code, rs.header.phrase)

        for name, value in rs.header.headers:
            self._response.headers[name] = value

        content = rs.get_body()

        if "Content-Encoding" in self._response.headers \
                and self._response.headers["Content-Encoding"] in DECOMPRESSOR:
            decompressor = DECOMPRESSOR[self._response.headers["Content-Encoding"]]()
            content = decompressor.decompress(content)
            del self._response.headers["Content-Encoding"]

        self._response.content = StringIO(content)

        if "Content-Length" in self._response.headers:
            # update Content-Length as the data may have been compressed
            self._response.headers["Content-Length"] = len(content)

        # we are now at the main thread, the callback call should occur at IO's
        cef.PostTask(cef.TID_IO, self._response_cb.Continue)

    def _init_from_request(self, request):
        kwargs = {
            "headers": request.GetHeaderMap(),
            "data": request.GetPostData(),
            "allow_redirects": False, # let cef deal with them
            "callback": partial(self._response_ready),
            "stream": True, # we need access to the raw response
        }

        self._request = grequests.request(request.GetMethod(), request.GetUrl(), **kwargs)
        grequests.send(self._request, self._request_handler._request_pool)

@strongref
class WARCRequestHandler(object):
    _current_warc = None
    _request_pool = None

    def __init__(self, current_warc=None):
        self._current_warc = current_warc
        self._request_pool = Pool(REQUEST_POOLSIZE)

    def GetResourceHandler(self, browser, frame, request):
        url = request.GetUrl()
        parser_url = urlparse(url)

        if parser_url.scheme not in ("http", "https"):
            return None # let to cef process

        warc_record = self._current_warc.find_record(url) if self._current_warc else None

        if warc_record:
            resource_handler = None

        else:
            resource_handler = WARCResourceHandler(self, request=request)
            self._AddStrongReference(resource_handler)

        return resource_handler

    @property
    def current_warc(self):
        return self._current_warc

    @current_warc.setter
    def current_warc(self, warc):
        self._current_warc = warc

class WARCResponse(object):
    url = None
    status_code = None
    status_text = None
    headers = None
    content = None

    def __init__(self, url, status_code, status_text):
        self.url = url
        self.status_code = status_code
        self.status_text = status_text
        self.headers = {}

    def is_redirect(self):
        return ("Location" in self.headers and self.status_code in (301, 302, 303, 307, 308))

class CefGreenlet(gevent.Greenlet):
    def __init__(self):
        super(self.__class__, self).__init__()

    def _run(self):
        while True:
            cef.MessageLoopWork()
            gevent.sleep(0.01)

if __name__ == "__main__":
    cef.Initialize()

    browser = cef.CreateBrowserSync()

    warc_file = os.path.join(WARC_DIR, "bardo-browser.warc.gz")
    current_warc = Warc(warc_file, temporary=True, main_url="http://google.com")

    req_handler = WARCRequestHandler(current_warc)

    browser.SetClientHandler(req_handler)

    def loop():
        while True:
            cef.MessageLoopWork()
            gevent.sleep(0.01)

    # XXX: obviously this is wrong
    req_handler._request_pool.spawn(loop)

    browser.GetMainFrame().LoadUrl("http://google.com")

    req_handler._request_pool.join()

    cef.Shutdown()
