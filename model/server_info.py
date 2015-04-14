from biicode.common import __version__
from biicode.common.utils.serializer import Serializer
from biicode.common.exception import BiiSerializationException
from biicode.common.utils.bii_logging import logger
import traceback


class ServerInfo(object):
    '''Placeholder for any info server should send to client in test_connection'''

    VERSION = 'v'
    COMPATIBLE = 'c'
    URL = 'u'
    MESSAGES = 'm'

    def __init__(self, version=None, message='', last_compatible="0"):
        self.version = ClientVersion(version) if version else ClientVersion(__version__)
        self.last_compatible = ClientVersion(last_compatible)
        self.download_url = ''
        try:
            # There was a str(message) here, but that is wrong, fails in Pydev
            self.messages = message.encode('utf-8')
        except UnicodeEncodeError:
            tb = traceback.format_exc()
            logger.error(tb)
            logger.error('Invalid server info message')
            self.messages = message.encode('ascii', 'ignore')

    def __repr__(self):
        return 'version: %s, last_compatible: %s' % (self.version, self.last_compatible)

    def serialize(self):
        return Serializer().build(
            (ServerInfo.VERSION, self.version),
            (ServerInfo.COMPATIBLE, self.last_compatible),
            (ServerInfo.URL, self.download_url),
            (ServerInfo.MESSAGES, self.messages),
            )

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) \
            and self.version == other.version \
            and self.last_compatible == other.last_compatible \
            and self.download_url == other.download_url \
            and self.messages == other.messages

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def deserialize(data):
        try:
            si = ServerInfo()
            si.version = ClientVersion(data[ServerInfo.VERSION])
            si.last_compatible = ClientVersion(data[ServerInfo.COMPATIBLE])
            si.download_url = data[ServerInfo.URL]
            si.messages = data[ServerInfo.MESSAGES]
            return si
        except Exception as e:
            raise BiiSerializationException(e)


class ClientVersion(object):
    def __init__(self, version):
        self.version = version

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.version == other.version

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.version

    def __lt__(self, other):
        if self.version == 'develop':
            return False
        if other.version == 'develop':
            return self.version != 'develop'
        sversions = self.version.split('.')
        oversions = other.version.split('.')
        max_index = min(len(sversions), len(oversions))
        for i in range(0, max_index):
            if int(sversions[i]) < int(oversions[i]):
                return True
            if int(sversions[i]) > int(oversions[i]):
                return False
        return len(sversions) < len(oversions)

    def __gt__(self, other):
        if self.version == 'develop':
            return other.version != 'develop'
        if other.version == 'develop':
            return False
        sversions = self.version.split('.')
        oversions = other.version.split('.')
        max_index = min(len(sversions), len(oversions))
        for i in range(0, max_index):
            if int(sversions[i]) > int(oversions[i]):
                return True
            if int(sversions[i]) < int(oversions[i]):
                return False
        return len(sversions) > len(oversions)

    def serialize(self):
        return self.version
