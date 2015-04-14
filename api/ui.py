from biicode.common.utils.bii_logging import logger as logger
from collections import namedtuple
from biicode.common.utils.serializer import ListDeserializer
from biicode.common.output_stream import LEVEL, INFO, DEBUG, WARN, ERROR


class Message(namedtuple('Message', 'msg level')):
    '''Messages that biiserver can send to the client
    A message contains a string an a criticality level'''

    def __repr__(self):
        return '%s: %s' % (LEVEL[self.level], self.msg)

    @staticmethod
    def deserialize(data):
        return Message(data[0], data[1])


class BiiResponse(list):
    '''Represents a response from the server, contains a collection of Message'''

    def debug(self, msg):
        logger.debug(">> DEBUG: %s" % msg)
        self.append(Message(msg, DEBUG))

    def info(self, msg):
        logger.debug(">> INFO: %s" % msg)
        self.append(Message(msg, INFO))

    def warn(self, msg):
        logger.debug(">> WARN: %s" % msg)
        self.append(Message(msg, WARN))

    def error(self, msg):
        logger.debug(">> ERROR: %s" % msg)
        self.append(Message(msg, ERROR))

    def __repr__(self):
        return '\n'.join([repr(x) for x in self])

    @staticmethod
    def deserialize(data):
        return BiiResponse(ListDeserializer(Message).deserialize(data))

    def biiout(self, output_stream):
        for msg in self:
            if msg.level == ERROR:
                output_stream.error(msg.msg)
            elif msg.level == WARN:
                output_stream.warn(msg.msg)
            elif msg.level == DEBUG:
                output_stream.debug(msg.msg)
            elif msg.level == INFO:
                output_stream.info(msg.msg)
