from collections import namedtuple
from biicode.common.utils.serializer import Serializer, ListDeserializer
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.resource import ResourceDeserializer
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.exception import BiiSerializationException
from biicode.common.model.cells import CellDeserializer
from biicode.common.model.content import ContentDeserializer
from biicode.common.model.id import ID
from biicode.common.edition.block_holder import BIICODE_FILE


ClosureItem = namedtuple('ClosureItem', 'resource version')


class Closure(dict):
    '''A connected set of resources {BlockCellName: (Resource, Version)}'''

    def add_item(self, resource, version, biiout):
        old_item = self.get(resource.name)
        #assert old_item.version != version if old_item else True, "Adding the same resource!"
        if old_item and old_item.resource != resource:
            biiout.error('Incompatible dependency "%s", different in versions:\n'
                           '%s and %s\n'
                           'Fix it adding the version you want to your "%s" file'
                            % (resource.name, version, old_item.version, BIICODE_FILE))
            biiout.warn('Using version "%s" while you fix it' % (old_item.version, ))
        else:
            self[resource.name] = ClosureItem(resource, version)

    SERIAL_NAMES = 'names'
    SERIAL_RESOURCES = 'resources'
    SERIAL_VERSIONS = 'versions'

    def serialize(self):
        if self:
            resources, versions = zip(*self.values())
        else:
            resources, versions = [], []
        ser = Serializer().build((Closure.SERIAL_NAMES, self.keys()),
                                 (Closure.SERIAL_RESOURCES, resources),
                                 (Closure.SERIAL_VERSIONS, versions))
        return ser

    @staticmethod
    def deserialize(data):
        try:
            names = ListDeserializer(BlockCellName).deserialize(data[Closure.SERIAL_NAMES])
            d = ResourceDeserializer(CellDeserializer(ID), ContentDeserializer(ID))
            resources = ListDeserializer(d).deserialize(data[Closure.SERIAL_RESOURCES])
            versions = ListDeserializer(BlockVersion).deserialize(data[Closure.SERIAL_VERSIONS])
            return Closure(dict(zip(names, zip(resources, versions))))
        except Exception as e:
            raise BiiSerializationException(e)
