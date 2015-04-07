import logging
from biicode.common.conf import BII_LOGGING_LEVEL, BII_LOGGING_FILE, BII_TRACE_ERRORS
import sys
from logging import StreamHandler
import traceback


class BiiHandler(StreamHandler):
    def emit(self, record):
        self.__do_ever_actions(record)

        if record.levelno == logging.ERROR:
            self.__do_error_actions(record)
        return super(BiiHandler, self).emit(record)

    def __do_ever_actions(self, record):
        #record.msg = "%i => %s" % (id(gevent.getcurrent()), record.msg)
        pass

    def __do_error_actions(self, record):
        if BII_TRACE_ERRORS:
            c = " ".join(traceback.format_stack())  # For more information in errors log
            try:
                record.msg += "\n----------%s" % c
            except:
                pass
        # CUSTOM ACTIONS LIKE SEND NOTIFICATIONS ETC
        # (in case we want to implement it and not to use alert system of heroky addons)
        pass


class MultiLineFormatter(logging.Formatter):
    def format(self, record):
        str_ = logging.Formatter.format(self, record)
        separator = record.message if record.message else None
        if separator is None:
            return separator
        header, _ = str_.split(separator)
        str_ = str_.replace('\n', '\n' + ' ' * len(header))
        return str_

logger = logging.getLogger('biicode')
if BII_LOGGING_FILE is not None:
    hdlr = logging.FileHandler(BII_LOGGING_FILE)
else:
    hdlr = BiiHandler(sys.stderr)

formatter = MultiLineFormatter('%(levelname)-6s:%(filename)-15s[%(lineno)d]: '
                               '%(message)s [%(asctime)s]')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(BII_LOGGING_LEVEL)


#CRITICAL = 50
#FATAL = CRITICAL
#ERROR = 40
#WARNING = 30
#WARN = WARNING
#INFO = 20
#DEBUG = 10
#NOTSET = 0
