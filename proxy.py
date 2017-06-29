import threading

from mitmproxy import http
from mitmproxy import options as moptions
from mitmproxy import controller, proxy, master
from mitmproxy.proxy import server

class MITMAddon:
    _current_warc = None

    def __init__(self, current_warc=None):
        self._current_warc = current_warc

    def request(self, flow):
       #flow.request.anticache()
 
        print("request")
 
        flow.response = http.HTTPResponse.make(
            200,
            b"Hello World",
            {"Content-Type": "text/html"}
        )

    def response(self, flow):
        print("response")

    @property
    def current_warc(self):
        return self._current_warc

    @current_warc.setter
    def current_warc(self, warc):
        self._current_warc = warc

class WARCProxyServer:
    _thread = None
    _mitm_master = None
    _current_warc = None
    _port = 0

    def __init__(self, current_warc=None):
        super().__init__()

        self._current_warc = current_warc

    def start(self):
        proxy_options = moptions.Options(
            no_upstream_cert=True,
            ssl_insecure=True,
            listen_host="127.0.0.1",
            listen_port=0, # let the os pick a random port
        )

        config = proxy.ProxyConfig(proxy_options)
        mitm_server = server.ProxyServer(config)

        self._mitm_master = master.Master(proxy_options, mitm_server)
        self._mitm_master.addons.add(MITMAddon(self._current_warc))
        self._port = mitm_server.socket.getsockname()[1]

        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self):
        try:
            self._mitm_master.shutdown()

        finally:
            self._port = 0

    @property
    def current_warc(self):
        return self._current_warc

    @current_warc.setter
    def current_warc(self, warc):
        self._current_warc = warc

    @property
    def port(self):
        return self._port

    def _run(self):
        self._mitm_master.run()

if __name__ == "__main__":
    wps = WARCProxyServer()
    wps.start()

    print("Listening on:", wps.port)
