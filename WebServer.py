from gevent.pywsgi import WSGIServer

from Web import create_app

try:
    print("Web Server Running!")
    http_server = WSGIServer(("0.0.0.0", 5000), create_app())
    http_server.serve_forever()
except KeyboardInterrupt:
    pass
