import collections
from biicode.common.utils.bii_logging import logger
from biicode.common.model.cells import VirtualCell
from biicode.common.edition.parsing.factory import parser_factory


def resource_diff_function(base, other):
    from biicode.common.model.content import content_diff
    from biicode.common.model.cells import cell_diff
    if not base:  # New item
        base = (None, None)
    if not other:  # Deleted item
        other = (None, None)

    rdiff = cell_diff(base[0], other[0])
    cdiff = content_diff(base[1], other[1])
    return Resource(rdiff, cdiff)


class Resource(collections.namedtuple('Resource', ['cell', 'content'])):
    def __new__(cls, cell=None, content=None):
        return super(Resource, cls).__new__(cls, cell, content)

    @property
    def name(self):
        return self.cell.name

    @property
    def cell_name(self):
        return self.cell.name.cell_name

    def parse(self, biiresponse):
        if isinstance(self.cell, VirtualCell):
            biiresponse.error("You're trying to parse a virtual file: %s" % self.cell.name)
            return False

        try:
            if self.content.parser is None:
                self.content.parser = parser_factory(self.cell.type, self.cell.name.cell_name)
            if self.content.parser:
                self.content.parse()
                self.cell.hasMain = self.content.parser.has_main_function()
                self.cell.dependencies.update_declarations(self.content.parser.explicit_declarations)
        except Exception as e:
            logger.error(str(e))
            biiresponse.error("Error parsing %s file" % self.cell.name)

    def similarity(self, other):
        if self.content is not None and other.content is not None:
            return self.content.similarity(other.content)
        return False


class ResourceDeserializer(object):
    def __init__(self, cell_deserializer, content_deserializer):
        self.cell_deserializer = cell_deserializer
        self.content_deserializer = content_deserializer

    def deserialize(self, data):
        return Resource(self.cell_deserializer.deserialize(data[0]),
                        self.content_deserializer.deserialize(data[1]))
