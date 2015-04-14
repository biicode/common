
class SystemCellName(str):
    def __new__(cls, value, validate=True):
        assert value is not None
        if validate:
            value = value.replace('\\', '/')
        obj = str.__new__(cls, value)
        return obj

    @staticmethod
    def deserialize(data):
        return SystemCellName(data, False)

    def serialize(self):
        return self[:]
