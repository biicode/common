from StringIO import StringIO
from colorama import Fore, Back, Style
import logging.handlers
from logging import Formatter
import os
DEBUG = 0
INFO = 1
WARN = 2
ERROR = 3
LEVEL = {DEBUG: 'DEBUG', INFO: 'INFO', WARN: 'WARN', ERROR: 'ERROR'}


class Color(object):
    RED = Fore.RED  # @UndefinedVariable
    WHITE = Fore.WHITE  # @UndefinedVariable
    CYAN = Fore.CYAN  # @UndefinedVariable
    GREEN = Fore.GREEN  # @UndefinedVariable
    MAGENTA = Fore.MAGENTA  # @UndefinedVariable
    BLUE = Fore.BLUE  # @UndefinedVariable
    YELLOW = Fore.YELLOW  # @UndefinedVariable
    BLACK = Fore.BLACK  # @UndefinedVariable

    BRIGHT_RED = Style.BRIGHT + Fore.RED  # @UndefinedVariable
    BRIGHT_BLUE = Style.BRIGHT + Fore.BLUE  # @UndefinedVariable
    BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW  # @UndefinedVariable
    BRIGHT_GREEN = Style.BRIGHT + Fore.GREEN  # @UndefinedVariable
    BRIGHT_CYAN = Style.BRIGHT + Fore.CYAN   # @UndefinedVariable
    BRIGHT_WHITE = Style.BRIGHT + Fore.WHITE   # @UndefinedVariable
    BRIGHT_MAGENTA = Style.BRIGHT + Fore.MAGENTA   # @UndefinedVariable

    BACK_YELLOW = Back.YELLOW  # @UndefinedVariable
    BACK_BLUE = Back.BLUE  # @UndefinedVariable
    BACK_BLACK = Back.BLACK  # @UndefinedVariable
    BACK_MAGENTA = Back.MAGENTA  # @UndefinedVariable
    BACK_CYAN = Back.CYAN  # @UndefinedVariable
    BACK_GREEN = Back.GREEN  # @UndefinedVariable
    BACK_RED = Back.RED  # @UndefinedVariable
    BACK_WHITE = Back.WHITE   # @UndefinedVariable


class OutputStream(object):
    '''Wraps an output stream, it can be constructed with sys.stdout, StringIO, cStringIO or any
    other file implementing class.
    It prints to a stream and, optionally, to a log file
    Useful for testing if you want to collect output across an execution.
    '''
    color = False

    def __init__(self, stream=None, log_file_name=None, level=INFO):
        '''
        Params:
            stream: if defined, ALL output will be logged to it'
            log_file_name: File where to store logs
            level: Logging level to display
        '''
        if stream is None:
            stream = StringIO()
        self.stream = stream
        self._level = level
        if log_file_name is not None:
            log_name = os.path.splitext(log_file_name)[0]
            self.logger = logging.getLogger(log_name)
            handler = logging.handlers.RotatingFileHandler(log_file_name,
                                                           maxBytes=10240,  # 10 Mb
                                                           backupCount=3)
            handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s', None))
            self.logger.addHandler(handler)
        else:
            self.logger = None

    def flush(self, truncate=True):
        try:
            self.stream.flush()
            if truncate:
                self.stream.truncate(0)
        except IOError as e:
            self.logger.log(logging.ERROR, str(e))

    def __repr__(self):
        if isinstance(self.stream, StringIO):
            return self.stream.getvalue()
        else:
            return repr(self.stream)

    def writeln(self, data, front=None, back=None):
        self.write(data, front, back, True)

    def write(self, data, front=None, back=None, newline=False):
        data = str(data)
        if OutputStream.color and (front or back):
            color = "%s%s" % (front or '', back or '')
            end = (Style.RESET_ALL + "\n") if newline else Style.RESET_ALL  # @UndefinedVariable
            self.stream.write("%s%s%s" % (color, data, end))
        else:
            if newline:
                data = "%s\n" % data
            self.stream.write(data)
        if self.logger:
            self.logger.info(data)

    ####################################################################
    # BASIC LOGGING-LIKE FUNCTIONS
    ####################################################################

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

    def log(self, data, level=DEBUG):
        if self._level <= level:
            if OutputStream.color:
                style = {DEBUG: Color.BRIGHT_BLUE,
                         WARN: Color.BRIGHT_YELLOW + Color.BACK_BLACK,
                         ERROR: Color.BRIGHT_RED}.get(level, '')
                self.stream.write('%s%s: %s%s\n' % (style, LEVEL[level], str(data),
                                                    Style.RESET_ALL))  # @UndefinedVariable
            else:
                self.stream.write('%s: %s\n' % (LEVEL[level], str(data)))
        if self.logger:
            self.logger.log(getattr(logging, LEVEL[level]), str(data))

    def info(self, data):
        self.log(data, INFO)

    def debug(self, data):
        self.log(data, DEBUG)

    def warn(self, data):
        self.log(data, WARN)

    def error(self, data):
        self.log(data, ERROR)
