# -*- coding: utf-8 -*-
import os
from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import tornado.web
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
from django.conf import settings

from requestlogger import WSGILogger


def log_formatter(status_code, environ, content_length, *, rt_us=None, **kwargs):
    rt_ms = rt_us / 1000.0
    now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return "{now_ts}:【{environ[REQUEST_METHOD]} {environ[PATH_INFO]} {status_code}】 ip={environ[REMOTE_ADDR]} [{rt_ms}ms]".format(**locals())

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

    execute_from_command_line(['manage.py', 'collectstatic', '--no-input'])

    application = get_wsgi_application()
    is_logging = True
    if is_logging:
        logging_app = WSGILogger(application, [], logger_name='wsgi', formatter=log_formatter)
        wsgi_app = tornado.wsgi.WSGIContainer(logging_app)
    else:
        wsgi_app = tornado.wsgi.WSGIContainer(application)
    STATIC_ROOT = settings.STATIC_ROOT
    MEDIA_ROOT = settings.MEDIA_ROOT
    print('static path:', STATIC_ROOT)
    print(' media path:', MEDIA_ROOT)
    handlers = [
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_ROOT}),
        (r'/media/(.*)', tornado.web.StaticFileHandler, {'path': MEDIA_ROOT}),
        (r'.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
    ]
    tornado_app = tornado.web.Application(handlers)
    http_server = tornado.httpserver.HTTPServer(tornado_app)
    port = 8000
    host = '0.0.0.0'
    print(' visit link: http: //{0}:{1}/'.format('127.0.0.1', port))
    http_server.listen(port, address=host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
