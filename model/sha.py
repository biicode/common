
import hashlib
import bson


class SHABuilder(object):
    def __init__(self, value=None):
        self.md = hashlib.sha1()
        if value:
            self.md.update(value)

    def __iadd__(self, item):
        if isinstance(item, (set, list, tuple)):
            for elem in sorted(item):
                self.md.update(elem)
        else:
            self.md.update(item)
        return self

    def sha(self):
        return SHA(self.md.hexdigest())


class SHA(str):
    '''IMportant: This class CANNOT implement __str__ for easy reading the string
    as it destroy the behaviour'''

    def __new__(cls, value):
        if value is None:
            return None
        return str.__new__(SHA, value)

    def __repr__(self):
        return self.encode('hex_codec')

    def serialize(self):
        return bson.Binary(self)

    @staticmethod
    def deserialize(data):
        return SHA(data)
