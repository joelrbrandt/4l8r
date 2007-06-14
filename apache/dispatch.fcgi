#!/usr/bin/python

# Load the WSGI application from the config file
from paste.deploy import loadapp
wsgi_app = loadapp('config:/usr/lib/cgi-bin/4l8r/production.ini')

# Deploy it using FastCGI
if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(wsgi_app).run()
