
class FixedString(str):

    def __new__(cls, value):
        if value is None:
            return None
        if not hasattr(cls, '_values'):
            cls._values = {v.upper(): v for v in cls.values}
        try:
            value = value.upper()
            obj = str.__new__(cls, cls._values[value])
            return obj
        except:
            raise ValueError('%s is not a valid %s. Possible values are %s'
                             % (value, cls.__name__, cls.values))

    def serialize(self):
        return str(self)

    @classmethod
    def deserialize(cls, data):
        return cls(data)

    def __eq__(self, other):
        if isinstance(other, basestring):
            other = self.__class__(other)
        return super(FixedString, self).__eq__(other)

    def __ne__(self, other):
        return not self == other


class FixedStringWithValue(FixedString):
    '''For having a fixedstring associated to a value.
       Expect a map_values class attribute with keys being the fixedstrings and values
       Example of use:

       class RestAction(UserTracedAction):
           map_values = {'GET_PUBLISHED_RESOURCES': 0, 'CREATE_BLOCK': 1, 'PUBLISH': 2}
    '''

    def __new__(cls, value):
        cls.values = cls.map_values.keys()
        obj = FixedString.__new__(cls, value)
        return obj

    @property
    def value(self):
        return self.__class__.map_values[self]
