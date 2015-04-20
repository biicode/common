#!/usr/bin/env python

from os import linesep
import zlib
from biicode.common.exception import BiiException
from biicode.common.diffmerge.differ import similarity
from biicode.common.utils.serializer import Serializer
from biicode.common.model.sha import SHABuilder, SHA


def compress(bufferArray):
    try:
        return zlib.compress(bufferArray)
    except IOError:
        raise BiiException("Error compressing load text string")


def uncompress(bufferArray):
    try:
        return zlib.decompress(bufferArray)
    except IOError:
        raise BiiException("Error compressing load text string")


def systemize_text(text):
    '''given a supposedly normalized text with only \n, create a OS specific version
    with the convenient linesep'''
    if linesep != '\n':
        text = text.replace(b'\n', linesep)
    return text


def normalize_text(text):
    '''given any text, tries to compute a normalized version containing only  \n. Might fail
    in some cases with \r, but this way should not be used to read user files, only for generated
    strings in biicode. For user files use the Blob(path=XXX) parameter, that uses 'rU' open
    mode'''

    # This in memory replace seems only to be 10% slower that directly reading from file with rU
    text = text.replace(b'\r\n', '\n')
    # FIXME: It is possible that \r\r\n exist in file
    text = text.replace(b'\r', '\n')
    #if not text.endswith('\n'):
    #    text = text + "\n"
    return text


class Blob(object):
    """IMPORTANT: This class overwrites serialization, so if you add extra field,
        REMEMBER TO PUT in read/write functions
    """

    SERIAL_SHA_KEY = "s"
    SERIAL_IS_BINARY_KEY = "b"
    SERIAL_COMPRESSED_BIN_KEY = "c"
    SERIAL_SIZE_KEY = "sz"

    def __init__(self, blob=None, is_binary=False, path=None):
        ''' public constructor with a string as parameter, there is no-guarantee that the input is
         really Sys-compliant, so better normalize it, so call setText(), no setNormalizedText()!!!
        '''
        self._binary = None  # The real load of the blob
        self._compressed_bin = None  # The load, but compressed
        self._sys_text = None  # Transient, the load text as system CRLF requires
        self._sha = None  # shas are also lazily computed
        self._is_binary = is_binary
        if blob is not None:
            assert path is None
            assert isinstance(blob, basestring)
            if is_binary:
                self._binary = blob
            else:
                self._binary = normalize_text(blob)
        if path is not None:
            assert blob is None
            if is_binary:
                with open(path, 'rb') as handle:
                    content = handle.read()
            else:
                with open(path, 'rU') as handle:
                    content = handle.read()
                    #At the moment we leave this end of file with \n here, cause some tests are
                    #broken otherwise
                    #if not content.endswith('\n'):
                    #    content = '%s\n' % content
                #This was in file_walker read blob, not sure why it was necessary
                #if content != load.load:
                    #TODO: Print warning to user, re-writing his file to be normalized
                    #file_utils.save(file_, load.load)
            self._binary = content
        self._size = None

    def __repr__(self):
        if self._is_binary:
            return "BinaryContent"
        return self.binary

    @property
    def bytes(self):
        return len(self.binary)

    # TODO: test
    def similarity(self, other):
        if self.sha == other.sha:
            return 1.0
        if self._is_binary:
            if self.binary == other.binary:
                return 1.0
            else:
                return 0.0
        return similarity(self.binary, other.binary)

    @property
    def is_binary(self):
        return self._is_binary

    @property
    def binary(self):
        if self._binary is None:
            self._binary = uncompress(self._compressed_bin)
        return self._binary

    @binary.setter
    def binary(self, binary):
        self._is_binary = True
        self._binary = binary
        self._compressed_bin = None
        self._sys_text = None
        self._sha = None

    @property
    def text(self):
        return self.binary

    @text.setter
    def text(self, text):
        self._is_binary = False
        self._binary = normalize_text(text)
        self._compressed_bin = None
        self._sys_text = None
        self._sha = None

    @property
    def load(self):
        if self._is_binary:
            return self.binary
        return self._system_text()

    @property
    def size(self):
        """size in bytes of content"""
        return len(self.binary)

    @property
    def unicode_load(self):
        return unicode(self.load, errors="ignore")

    def _system_text(self):
        """ performs a replacement if necessary of LF to the CRLF
            @return a string with the CRLF combination specific for the current OS
        """
        if self._sys_text is None:
            self._sys_text = systemize_text(self.text)
        return self._sys_text

    @property
    def sha(self):
        if self._sha is None:
            self._sha = SHABuilder(self.binary).sha()
        return self._sha

    def _compressed(self):
        if self._compressed_bin is None:
            self._compressed_bin = compress(self._binary)
        return self._compressed_bin

    def __hash__(self):
        return hash(self.sha)

    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, self.__class__):
            return self.sha == other.sha
        return False

    def __ne__(self, other):
        return not self == other

    def replace(self, origin, newString):
        t = self.text.replace(origin, newString)
        self.text = t
        # Just in case the replace introduced bad CRLF

    def __len__(self):
        return len(self.binary)

    def serialize(self):
        from bson import Binary  # by pymongo
        bson = Binary(self._compressed())
        return Serializer().build(
                    (Blob.SERIAL_SHA_KEY, self.sha),
                    (Blob.SERIAL_IS_BINARY_KEY, self._is_binary),
                    (Blob.SERIAL_SIZE_KEY, self.size),
                    (Blob.SERIAL_COMPRESSED_BIN_KEY, bson)
        )

    @staticmethod
    def deserialize(data):
        is_binary = data[Blob.SERIAL_IS_BINARY_KEY]
        c = Blob(is_binary=is_binary)
        c._compressed_bin = data[Blob.SERIAL_COMPRESSED_BIN_KEY]
        c._size = data.get(Blob.SERIAL_SIZE_KEY)
        #c.is_binary = data[Blob.SERIAL_IS_BINARY_KEY]
        c._sha = SHA.deserialize(data[Blob.SERIAL_SHA_KEY])
        return c
