from collections import namedtuple
from collections import defaultdict

from biicode.common.model.brl.cell_name import CellName
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.utils.serializer import DictDeserializer, SetDeserializer
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.resource import ResourceDeserializer
from biicode.common.model.cells import CellDeserializer
from biicode.common.model.content import ContentDeserializer
from biicode.common.model.id import ID
from biicode.common.model.declare.declaration import Declaration
import copy


class VersionDict(defaultdict):
    def __init__(self, items_type):
        super(VersionDict, self).__init__(items_type)

    def explode(self):
        items_type = self.default_factory()
        if isinstance(items_type, (set, list, tuple)):
            result = []
            for k, v in self.iteritems():
                result.extend([Reference(k, x) for x in v])
            return result
        elif isinstance(items_type, dict):
            result = {}
            for k, v in self.iteritems():
                for k2, v2 in v.iteritems():
                    result[Reference(k, k2)] = v2
            return result
        raise ValueError('This type of VersionDict cannot be exploded')

    def __repr__(self):
        result = [str(self.__class__.__name__)]
        for k, v in self.iteritems():
            result.append('%s: %s' % (k, v))
        return ', '.join(result)


class AbsoluteReferences(VersionDict):
    """{block_version: set(BlockCellName)}
    """
    def __init__(self):
        super(AbsoluteReferences, self).__init__(set)


class References(VersionDict):
    '''Dict of block_version -> Set[CellName]. It can also be
      {block_version: Set of BlockCellName}, for Dependencies translating with DependencyTranslator
    '''

    def __init__(self):
        super(References, self).__init__(set)

    def add(self, reference):
        self[reference.block_version].add(reference.ref)

    def __deepcopy__(self, memo):
        '''this method is necessary for deepcopy in memory caches, defaultdict
        deepcopy __init__ signature is incompatible with current'''
        r = References()
        for key, values in self.iteritems():
            r[key] = copy.deepcopy(values)
        return r

    @staticmethod
    def deserialize(data):
        if data is None:
            return None
        d = DictDeserializer(BlockVersion, SetDeserializer(CellName)).deserialize(data)
        result = References()
        result.update(d)
        return result


class ReferencedResources(VersionDict):
    '''The dict items are dict {CellName: Resource(Cell, Content)}'''
    def __init__(self):
        super(ReferencedResources, self).__init__(dict)

    @staticmethod
    def deserialize(data):
        d = DictDeserializer(BlockVersion,
                             DictDeserializer(CellName,
                                              ResourceDeserializer(CellDeserializer(ID),
                                                                   ContentDeserializer(ID)))).deserialize(data)
        result = ReferencedResources()
        result.update(d)
        return result

    def __add__(self, other):
        '''adds two referencedResources, for example localDb+remotes for building Snapshot of
        dependencies'''
        result = ReferencedResources()
        for version, deps in self.iteritems():
            result[version].update(deps)
        for version, deps in other.iteritems():
            result[version].update(deps)

        return result


class ReferencedDependencies(VersionDict):
    '''The dict items are dict{Declaration: set(BlockCellName)}'''
    def __init__(self):
        super(ReferencedDependencies, self).__init__(lambda: defaultdict(set))

    @staticmethod
    def deserialize(data):
        d = DictDeserializer(BlockVersion,
                             DictDeserializer(Declaration,
                                              SetDeserializer(BlockCellName))).deserialize(data)
        result = ReferencedDependencies()
        result.update(d)
        return result


class Reference(namedtuple('Reference', ['block_version', 'ref'])):
    '''Ref can only be a single ref
    '''

    def __repr__(self):
        return "%s/%s" % (self[0], self[1])

    @staticmethod
    def deserialize(data):
        return Reference(BlockVersion.deserialize(data[0]), CellName.deserialize(data[1]))

    def serialize(self):
        return (self.block_version.serialize(), self.ref)

    def block_cell_name(self):
        '''assuming that ref is a single CellName'''
        return self.block_version.block_name + self.ref
