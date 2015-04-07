#!/usr/bin/env python
# package: com.biicode.model

from biicode.common.utils.serializer import SetDeserializer, Serializer, DictDeserializer
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.declaration import Declaration
from biicode.common.model.deps_props import DependenciesProperties


class DependencySet(object):
    '''Class to represent the dependencies of a cell'''

    def __init__(self):
        self.explicit = set()  # BlockCellNames, obtained from code
        self.implicit = set()  # of BlockCellName, deduced implicitly
        self.system = set()  # of SystemResourceName, from code
        self.properties = DependenciesProperties()
        self.resolved = set()  # of DependencyDeclaration, found
        self.unresolved = set()  # of DependencyDeclaration, not found
        self.cell_name = None  # transient, not serializable name of cell. Required for relative
        self.paths = {}  # {Order, BlockNamePath} to help define order; used for include_paths

    def __eq__(self, other):
        # necessary equality comparison for "compare" operations between Resources
        return (self.explicit == other.explicit and
                self.implicit == other.implicit and
                self.system == other.system and
                self.properties == other.properties and
                self.resolved == other.resolved and
                self.unresolved == other.unresolved and
                self.paths == other.paths)

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_path(self, path_tuple):
        if path_tuple:
            order, path = path_tuple
            self.paths[order] = path

    @property
    def targets(self):
        return self.explicit.union(self.implicit)

    @property
    def data(self):
        '''obtain the data items, deducing it from properties'''
        return set([k for k, v in self.properties.iteritems()
                            if DependenciesProperties.DATA in v])

    @property
    def exclude_from_build(self):
        '''obtain the excluded items, deducing it from properties'''
        return set([k for k, v in self.properties.iteritems()
                            if DependenciesProperties.EXCLUDE_FROM_BUILD in v])

    def update_declarations(self, declarations):
        '''declarations: iterable of declarations explicitly found while parsing the file,
        When the new declarations are updated, as a result of a file parse, the whole
        dependencies are reset, and they are started from scratch, re-generated
        in the process'''
        self.explicit = set()
        self.implicit = set()
        self.system = set()
        self.properties = DependenciesProperties()
        self.resolved = set()
        self.unresolved = declarations
        self.paths = {}

    def _force_properties_support(self):
        '''those properties not supported by any target are removed'''
        targets = self.targets
        for block_cell_name in self.properties.keys():
            if block_cell_name not in targets:
                self.properties.pop(block_cell_name)

    def resolve(self, declaration, targets):
        self.unresolved.remove(declaration)
        self.resolved.add(declaration)
        self.explicit.update(targets)
        for target in targets:
            self.properties.add_properties(target, declaration.properties)

    def resolve_system(self, declaration, targets):
        self.unresolved.remove(declaration)
        self.resolved.add(declaration)
        self.system.update(targets)

    def update(self, other):
        ''' Updates current dependency set with other elements
        Params:
            updated_items: DependencySet
        Returns: Self
        '''
        self.explicit.update(other.explicit)
        self.implicit.update(other.implicit)
        self.system.update(other.system)
        self.resolved.update(other.resolved)
        self.unresolved.update(other.unresolved)
        self.paths.update(other.paths)
        for k, v in other.properties.iteritems():
            self.properties.add_properties(k, v)

        return self

    def update_resolved(self, resolved_items, renames):
        '''Updates dependency set with resolved dependencies.
        Params:
            resolved_items: dict{Declaration: Set(BlockCellName)
            renames {old:new}
        '''
        old_explicit = self.explicit.copy()
        resolved_declarations = resolved_items.keys()
        old_resolved = self.resolved.copy()
        # First remove from current explicit and resolved
        self.resolved.difference_update(resolved_declarations)

        '''those explicit dependencies not supported by any declaration are removed'''
        targets = set()
        for resolved in self.resolved:
            targets.update(resolved.match(self.explicit, self.cell_name))
        unsupported = self.explicit.difference(targets)
        self.explicit.difference_update(unsupported)
        self.properties.discard(unsupported)

        # now add again new resolved
        for declaration, targets in resolved_items.iteritems():
            if declaration in old_resolved:
                declaration.name = renames.get(declaration.name, declaration.name)
                self.resolved.add(declaration)
                self.explicit.update(targets)
                for target in targets:
                    self.properties.add_properties(target, declaration.properties)
        return old_explicit != self.explicit

    def add_implicit(self, block_cell_name):
        result = block_cell_name not in self.implicit
        self.implicit.add(block_cell_name)
        return result

    def __repr__(self):
        result = []
        result.append('Explicit %s' % self.explicit)
        result.append('Implicit %s' % self.implicit)
        result.append('Props %s' % self.properties)
        result.append('System %s' % self.system)
        result.append('Resolved %s' % self.resolved)
        result.append('Unresolved %s' % self.unresolved)
        result.append('Paths %s' % self.paths)
        return ' '.join(result)

    SERIAL_EXPLICIT = 'e'
    SERIAL_IMPLICIT = 'i'
    SERIAL_DATA = 'd'
    SERIAL_SYSTEM = 's'
    SERIAL_RESOLVED = 'r'
    SERIAL_UNRESOLVED = 'u'
    SERIAL_EXCLUDE = 'ex'
    SERIAL_PROPERTIES = 'p'
    SERIAL_PATHS = 'q'

    def serialize(self):
        return  Serializer().build(
                                  (DependencySet.SERIAL_EXPLICIT, self.explicit),
                                  (DependencySet.SERIAL_IMPLICIT, self.implicit),
                                  (DependencySet.SERIAL_PROPERTIES, self.properties),
                                  (DependencySet.SERIAL_SYSTEM, self.system),
                                  (DependencySet.SERIAL_RESOLVED, self.resolved),
                                  (DependencySet.SERIAL_UNRESOLVED, self.unresolved),
                                  (DependencySet.SERIAL_PATHS, self.paths),
                                  )

    targets_deserializer = SetDeserializer(BlockCellName)
    declaration_deserializer = SetDeserializer(Declaration)

    @staticmethod
    def deserialize(data):
        targets_deserializer = DependencySet.targets_deserializer
        declaration_deserializer = DependencySet.declaration_deserializer
        r = DependencySet()
        r.explicit = targets_deserializer.deserialize(data[DependencySet.SERIAL_EXPLICIT])
        r.implicit = targets_deserializer.deserialize(data[DependencySet.SERIAL_IMPLICIT])
        r.system = SetDeserializer(SystemCellName).deserialize(data[DependencySet.SERIAL_SYSTEM])
        r.resolved = declaration_deserializer.deserialize(data[DependencySet.SERIAL_RESOLVED])
        r.unresolved = declaration_deserializer.deserialize(data[DependencySet.SERIAL_UNRESOLVED])
        try:
            d = data[DependencySet.SERIAL_PROPERTIES]
            r.properties = DependenciesProperties.deserialize(d)
        except KeyError:
            pass

        try:
            d = data[DependencySet.SERIAL_PATHS]
            r.paths = DictDeserializer(int, str).deserialize(d)
        except KeyError:
            pass

        # This 2 latter are backward compatibility deserializations
        # TODO: Can be removed with a migration
        try:
            d = data[DependencySet.SERIAL_DATA]
            items = targets_deserializer.deserialize(d)
            for item in items:
                r.explicit.add(item)
                r.properties.add_property(item, DependenciesProperties.DATA)
        except KeyError:
            pass

        try:
            d = data[DependencySet.SERIAL_EXCLUDE]
            items = targets_deserializer.deserialize(d)
            for item in items:
                r.properties.add_property(item, DependenciesProperties.EXCLUDE_FROM_BUILD)
        except KeyError:
            pass
        return r
