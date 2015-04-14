import os
import re
from biicode.common.exception import InvalidNameException


class CellName(str):
    """ Class to define a normalized biicode file name path/to/file.h
    """
    pattern = re.compile("^[^\s*]+$")

    def __new__(cls, name, validate=True):
        if validate:
            name = name.strip().replace('\\', '/')
            if CellName.pattern.match(name) is None:
                raise InvalidNameException("'%s' is an invalid name" % name)
            _, ext = os.path.splitext(name)
            ext = ext.lower()
            obj = str.__new__(cls, name)
            obj._ext = ext
        else:
            obj = str.__new__(cls, name)
        return obj

    @property
    def extension(self):
        try:
            return self._ext
        except:
            _, ext = os.path.splitext(self)
            self._ext = ext.lower()
            return self._ext

    @property
    def path(self):
        try:
            return self._path
        except:
            self._path, _ = os.path.split(self)
            return self._path

    def serialize(self):
        return self[:]

    @staticmethod
    def deserialize(data):
        return CellName(data, False)
