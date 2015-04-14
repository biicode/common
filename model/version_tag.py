class VersionTag(int):

    def __new__(cls, value):
        if value < 0 or value > 3:
            raise ValueError('%s is not a valid VersionTag value it should be in [0, 3]')
        obj = int.__new__(cls, value)
        return obj

    def __repr__(self):
        return {0: "DEV", 1: "ALPHA", 2: "BETA", 3: "STABLE"}[self]

    def __str__(self):
        return repr(self)

    @classmethod
    def loads(cls, text):
        assert isinstance(text, str)
        values = {"DEV": 0, "ALPHA": 1, "BETA": 2, "STABLE": 3}
        try:
            value = values[text.upper()]
            return cls(value)
        except KeyError:
            raise ValueError("%s is not a valid tag it should be one of %s" % (text,
                                                                               values.keys()))

    @classmethod
    def deserialize(cls, data):
        return cls(data)

    def serialize(self):
        return int(self)

DEV = VersionTag(0)
ALPHA = VersionTag(1)
BETA = VersionTag(2)
STABLE = VersionTag(3)
