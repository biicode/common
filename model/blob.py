from os import linesep
import zlib
from biicode.common.exception import BiiException
from biicode.common.diffmerge.differ import similarity
from biicode.common.utils.serializer import Serializer
from biicode.common.model.sha import SHABuilder, SHA


class Blob(object):
    """ Object to hold content bytes, and manage lazy compression
    """

    def __init__(self, blob=None, is_binary=False):
        '''
        param blob: str object containing bytes, used as byte array or text string
        param is_binary: if True, nothing will be done, normalization to LF otherwise
        '''
        self._compressed_bin = None  # The load, but compressed
        self._sys_text = None  # Transient, the load text as system CRLF requires
        self._sha = None  # shas are also lazily computed
        self._is_binary = is_binary
        # The real load of the blob
        if is_binary:
            self._binary = blob
        elif blob is not None:
            assert isinstance(blob, basestring)
            self._binary = blob.replace(b'\r\n', '\n').replace(b'\r', '\n')
        else:
            self._binary = None
        self._size = None
        self.serialize_bytes = True

    def similarity(self, other):
        """ compares similarity for text blobs
        returns: if binary content return 1 if equal 0 otherwise
                 if text content return 0.0-1.0 of % of equal lines
        """
        if self.sha == other.sha:
            return 1.0
        if self._is_binary:
            if self.bytes == other.bytes:
                return 1.0
            else:
                return 0.0
        return similarity(self.bytes, other.bytes)

    @property
    def is_binary(self):
        return self._is_binary

    @property
    def bytes(self):
        """ obtain byte load, with lazy decompression from zipped array if necessary
        """
        if self._binary is None:
            try:
                self._binary = zlib.decompress(self._compressed_bin)
            except IOError:
                raise BiiException("Error compressing load text string")
        return self._binary

    @property
    def text(self):
        """ temporary method, to avoid fixing 100s of tests
        """
        # TODO: delete method and update tests
        return self.bytes

    @property
    def load(self):
        """ get the actual content that must be saved in disk
        """
        if self._is_binary:
            return self.bytes
        #performs a replacement if necessary of LF to the CRLF
        #    @return a string with the CRLF combination specific for the current OS
        if self._sys_text is None:
            if linesep != '\n':
                self._sys_text = self.bytes.replace(b'\n', linesep)
            else:
                self._sys_text = self.bytes
        return self._sys_text

    @property
    def unicode_load(self):
        """ get the actual content to be shown in web
        """
        return unicode(self.load, errors="ignore")

    @property
    def sha(self):
        """ get the sha of this blob, compute lazily if necessary
        """
        if self._sha is None:
            self._sha = SHABuilder(self.bytes).sha()
        return self._sha

    def __hash__(self):
        return hash(self.sha)

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, self.__class__):
            return self.sha == other.sha
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.bytes)

    @property
    def size(self):
        """size in bytes of content"""
        return len(self.bytes)

    def __repr__(self):
        if self._is_binary:
            return "BinaryContent"
        return self.bytes

    SERIAL_SHA_KEY = "s"
    SERIAL_IS_BINARY_KEY = "b"
    SERIAL_COMPRESSED_BIN_KEY = "c"
    SERIAL_SIZE_KEY = "sz"

    def serialize(self):
        if self.serialize_bytes:
            from bson import Binary  # by pymongo
            if self._compressed_bin is None:
                try:
                    self._compressed_bin = zlib.compress(self._binary)
                except IOError:
                    raise BiiException("Error compressing load text string")
            bson = Binary(self._compressed_bin)
            return Serializer().build(
                        (Blob.SERIAL_SHA_KEY, self.sha),
                        (Blob.SERIAL_IS_BINARY_KEY, self._is_binary),
                        (Blob.SERIAL_SIZE_KEY, self.size),
                        (Blob.SERIAL_COMPRESSED_BIN_KEY, bson)
            )
        else:
            return Serializer().build(
                        (Blob.SERIAL_SHA_KEY, self.sha),
                        (Blob.SERIAL_IS_BINARY_KEY, self._is_binary)
            )

    @staticmethod
    def deserialize(data):
        is_binary = data[Blob.SERIAL_IS_BINARY_KEY]
        c = Blob(is_binary=is_binary)
        try:
            c._compressed_bin = data[Blob.SERIAL_COMPRESSED_BIN_KEY]
            c._size = data.get(Blob.SERIAL_SIZE_KEY)
        except KeyError:
            pass
        c._sha = SHA.deserialize(data[Blob.SERIAL_SHA_KEY])
        return c
