# -*- coding: utf-8 -*-
"""
    from: https://github.com/pklaus/wsgi-request-logger
    refer: https://stackoverflow.com/questions/40438286/how-do-i-customize-tornados-access-logs/40446814#40446814
    Source: http://docs.python.org/3/library/datetime.html → "Example tzinfo classes"
    Idea:   http://stackoverflow.com/a/2071364/183995
"""
from datetime import datetime as dt, tzinfo, timedelta
import time as _time
import logging

try:
    clock = _time.perf_counter
except AttributeError:
    clock = _time.time

ZERO = timedelta(0)

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

Local = LocalTimezone()

class WSGILogger(object):
    """ This is the generalized WSGI middleware for any style request logging. """

    def __init__(self, application, handlers, logger_name='requestlogger', formatter=None, propagate=True, ip_header=None, **kwargs):
        self.formatter = formatter or WSGILogger.standard_formatter
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = propagate
        self.logger.setLevel(logging.DEBUG)
        for handler in handlers:
            self.logger.addHandler(handler)
        self.ip_header = ip_header
        self.application = application

    def __call__(self, environ, start_response):
        start = clock()
        status_codes = []
        content_lengths = []

        def custom_start_response(status, response_headers, exc_info=None):
            status_codes.append(int(status.partition(' ')[0]))
            for name, value in response_headers:
                if name.lower() == 'content-length':
                    content_lengths.append(int(value))
                    break
            return start_response(status, response_headers, exc_info)
        retval = self.application(environ, custom_start_response)
        runtime = int((clock() - start) * 10**6)
        content_length = content_lengths[0] if content_lengths else len(b''.join(retval))
        msg = self.formatter(status_codes[0], environ, content_length, ip_header=self.ip_header, rt_us=runtime)
        self.logger.info(msg)
        return retval

    @staticmethod
    def standard_formatter(status_code, environ, content_length):
        return "{0} {1}".format(dt.now().isoformat(), status_code)


def ApacheFormatter(with_response_time=True):
    """ A factory that returns the wanted formatter """
    if with_response_time:
        return ApacheFormatters.format_with_response_time
    else:
        return ApacheFormatters.format_NCSA_log


class ApacheFormatters(object):
    @staticmethod
    def format_NCSA_log(status_code, environ, content_length, **kwargs):
        """
          Apache log format 'NCSA extended/combined log':
          "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""
          see http://httpd.apache.org/docs/current/mod/mod_log_config.html#formats
        """
        
        # Let's collect log values
        val = dict()
        ip_header = kwargs.get('ip_header', None)
        if ip_header:
            try:
                val['host'] = environ.get(ip_header, '')
            except:
                val['host'] = environ.get('REMOTE_ADDR', '')
        else:
            val['host'] = environ.get('REMOTE_ADDR', '')
        val['logname'] = '-'
        val['user'] = '-'
        date = dt.now(tz=Local)
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][date.month - 1]
        val['time'] = date.strftime("%d/{0}/%Y:%H:%M:%S %z".format(month))
        val['request'] = "{0} {1} {2}".format(
              environ.get('REQUEST_METHOD', ''),
              environ.get('PATH_INFO', ''),
              environ.get('SERVER_PROTOCOL', '')
            )
        val['status'] = status_code
        val['size'] = content_length
        val['referer'] = environ.get('HTTP_REFERER', '')
        val['agent'] = environ.get('HTTP_USER_AGENT', '')
        
        # see http://docs.python.org/3/library/string.html#format-string-syntax
        FORMAT = '{host} {logname} {user} [{time}] "{request}" '
        FORMAT += '{status} {size} "{referer}" "{agent}"'
        return FORMAT.format(**val)

    @staticmethod
    def format_with_response_time(*args, **kwargs):
        """
          The dict kwargs should contain 'rt_us', the response time in milliseconds.
          This is the format for TinyLogAnalyzer:
          https://pypi.python.org/pypi/TinyLogAnalyzer
        """
        rt_us = kwargs.get('rt_us')
        return ApacheFormatters.format_NCSA_log(*args, **kwargs) + " {0}/{1}".format(int(rt_us/1000000), rt_us)


def log(handlers, formatter=ApacheFormatter(), **kwargs):
    """Decorator for logging middleware."""
    def decorator(application):
        return WSGILogger(application, handlers, **kwargs)
    return decorator
