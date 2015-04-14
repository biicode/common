from struct import pack, unpack
from bson.binary import Binary


def UserID(value):
    return ID((value, ))


class ID(tuple):
    """ ID is a tuple of integers used as table key indices
    """

    def __repr__(self):
        return ':'.join([str(i) for i in self])

    def __add__(self, value):
        # Override to add an integer
        assert isinstance(value, int), 'Wrong value %s' % value
        return ID(super(ID, self).__add__((value, )))

    @property
    def parent(self):
        return ID(self[:-1])

    def serialize(self):
        return Binary(pack('>%sI' % len(self), *self))

    @classmethod
    def deserialize(cls, data):
        if data is None:
            return None
        tup = unpack('>%sI' % (len(data) / 4), data)
        return cls(tup)
