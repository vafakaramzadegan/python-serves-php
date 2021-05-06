'''
    Python serves PHP
    --------------------------------------------
    A simple web server for PHP. just a wrapper
    for python's HTTPServer.

    Author: Vafa Karamzadegan
    https://github.com/vafakaramzadegan/EasyDraw
'''

from http.server import HTTPServer
from core.http_server import HttpServer
from core.config import server_config
from socketserver import ThreadingMixIn


# Handle requests in a separate thread.
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer): pass

# init server
httpd = ThreadedHTTPServer(
    ("localhost", server_config.ssl_port if server_config.use_ssl else server_config.server_port),
    HttpServer
)

# use ssl if enabled
if server_config.use_ssl:
    import ssl
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        server_side=True,
        certfile=server_config.cert_file,
        keyfile=server_config.key_file
    ) 

try:
    print("Server started, press <Ctrl-C> to stop.")
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.server_close()
    print("Server stopped.")