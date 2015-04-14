
class Version(str):
    SEPARATOR = '.'

    def __new__(cls, version=""):
        obj = str.__new__(cls, version)
        obj._list = None
        return obj

    @property
    def list(self):
        if self._list is None:
            self._list = []
            for item in self.split(Version.SEPARATOR):
                self._list.append(int(item) if item.isdigit() else item)
        return self._list

    def serialize(self):
        return str(self)

    @staticmethod
    def deserialize(data):
        if not data:
            return None
        return Version(data)

    def __cmp__(self, other):
        if other is None:
            return cmp(self.list, None)
        if isinstance(other, basestring):
            other = Version(other)
        return cmp(self.list, other.list)

    def __gt__(self, other):
        return cmp(self, other) == 1

    def __lt__(self, other):
        return cmp(self, other) == -1

    def __le__(self, other):
        c = cmp(self, other)
        return c in [0, -1]

    def __ge__(self, other):
        c = cmp(self, other)
        return c in [0, 1]
