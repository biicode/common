
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.utils.serializer import DictDeserializer, SetDeserializer


class DependenciesProperties(dict):
    '''{BlockCellName: set(Properties)}'''
    #Properties of dependencies
    DATA = 'd'
    EXCLUDE_FROM_BUILD = 'x'
    IMPLICIT = 'i'  # Not used yet

    def discard(self, targets):
        for target in targets:
            self.pop(target, None)

    def remove_property(self, target, prop):
        properties = self.get(target)
        if properties:
            properties.discard(prop)

    def add_property(self, target, prop):
        self.setdefault(target, set())
        self[target].add(prop)

    def add_properties(self, target, properties):
        if not properties:
            return
        self.setdefault(target, set())
        self[target].update(properties)

    @staticmethod
    def deserialize(data):
        if data is None:
            return None
        d = DictDeserializer(BlockCellName,
                             SetDeserializer(str)).deserialize(data)
        return DependenciesProperties(d)
