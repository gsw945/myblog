# -*- coding: utf-8 -*-
import os
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
from django.core.wsgi import get_wsgi_application


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
    application = get_wsgi_application()
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    port = 8000
    host = '0.0.0.0'
    print('visit by: [http: //{0}:{1}/]'.format(host, port))
    http_server.listen(port, address=host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
