import os
import io
import sys

from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
execute_from_command_line(['manage.py', 'collectstatic', '--no-input'])
# application = get_wsgi_application()

from twisted.python import threadpool
from twisted.internet import reactor
thpool = threadpool.ThreadPool(minthreads=25, maxthreads=81)

from zope.interface import provider
from twisted.logger import (
    globalLogPublisher, LogLevel, textFileLogObserver, ILogObserver,
    FilteringLogObserver, LogLevelFilterPredicate
)
from hendrix.deploy.base import HendrixDeploy


deployer = HendrixDeploy(
    action='start',
    options={
        'verbosity': 2,
        'http_port': 8000,
        # 'wsgi': application,
        'settings': os.environ['DJANGO_SETTINGS_MODULE']
    },
    reactor=reactor,
    threadpool=thpool
)
is_logging = True
is_log2file = False
if is_logging:
    if is_log2file:
        DEFAULT_LOG_FILE = os.path.join(settings.BASE_DIR, 'default-hendrix.log')

        @provider(ILogObserver)
        def FileObserver(path=DEFAULT_LOG_FILE, log_level=LogLevel.warn):
            file_observer = textFileLogObserver(io.open(path, 'at'))
            return FilteringLogObserver(
                file_observer,
                [LogLevelFilterPredicate(log_level), ]
            )
        log_path = os.path.join(settings.BASE_DIR, 'hendrix-debug.log')
        globalLogPublisher.addObserver(FileObserver(path=log_path, log_level=LogLevel.debug))
    else:
        @provider(ILogObserver)
        def ConsoleObserver(log_level=LogLevel.warn):
            console_observer = textFileLogObserver(sys.stdout)
            return FilteringLogObserver(
                console_observer,
                [LogLevelFilterPredicate(log_level), ]
            )

        globalLogPublisher.addObserver(ConsoleObserver(log_level=LogLevel.debug))
deployer.run()
