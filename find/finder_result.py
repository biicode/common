from biicode.common.utils.serializer import Serializer, SetDeserializer
from biicode.common.model.symbolic.reference import ReferencedDependencies
from biicode.common.model.declare.declaration import Declaration


class FinderResult(object):

    SERIAL_RESOLVED_KEY = "r"
    SERIAL_UNRESOLVED_KEY = "u"
    SERIAL_UPDATED_KEY = "a"
    SERIAL_RESPONSE_KEY = "f"

    def __init__(self):
        self.resolved = ReferencedDependencies()
        self.unresolved = set()
        self.updated = ReferencedDependencies()

    def __repr__(self):
        builder = ['FindResult']
        if self.resolved:
            builder.append('Resolved %s' % self.resolved)
        if self.unresolved:
            builder.append('UnResolved %s' % self.unresolved)
        if self.updated:
            builder.append("Updated: %s\n" % self.updated)
        return '\n'.join(builder)

    def __len__(self):
        return len(self.resolved) + len(self.updated)

    @staticmethod
    def deserialize(data):
        '''From dictionary to object FinderResult'''
        ret = FinderResult()
        if data == None:
            return ret
        ret.unresolved = SetDeserializer(Declaration).deserialize(data[FinderResult.SERIAL_UNRESOLVED_KEY])
        ret.resolved = ReferencedDependencies.deserialize(data[FinderResult.SERIAL_RESOLVED_KEY])
        ret.updated = ReferencedDependencies.deserialize(data[FinderResult.SERIAL_UPDATED_KEY])
        return ret

    def serialize(self):
        return  Serializer().build((FinderResult.SERIAL_UNRESOLVED_KEY, self.unresolved),
                                 (FinderResult.SERIAL_RESOLVED_KEY, self.resolved),
                                 (FinderResult.SERIAL_UPDATED_KEY, self.updated))

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) \
            and (other.resolved == self.resolved) \
            and (other.unresolved == self.unresolved) \
            and (other.updated == self.updated)

    def __ne__(self, other):
        return not self == other

    @property
    def update_renames(self):
        renames = {}
        for dep_dict in self.updated.itervalues():
            for declaration, block_cell_names in dep_dict.iteritems():
                if not '*' in declaration.name:
                    #TODO: What to do with python multiple imports
                    new_declaration = declaration.normalize(block_cell_names)
                    if new_declaration:
                        v = [v for v in block_cell_names if '__init__.py' not in v]
                        if len(v) == 1:
                            renames[declaration] = new_declaration
        return renames
