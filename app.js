var socket = new WebSocket("ws://localhost:" + serverPort);

socket.onopen = function() {
    new QWebChannel(socket, function (channel) {
        window.app = channel.objects.app;

        window.app.test();
    });
}
