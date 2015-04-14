from biicode.common.utils.serializer import Serializer
from biicode.common.exception import BiiSerializationException
from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.symbolic.reference import References
from biicode.common.deps.closure import Closure


class HiveDependencies(object):
    """ This is a caching object for storing the block and version level dependencies of the
    current graph, as well as the closure
    """
    def __init__(self):
        self.dep_table = None  # BlockVersionTable()
        self.references = None  # References()
        # TODO: The whole closure is being serialized. Check performance, improve
        self.closure = Closure()  # {BlockCellName: Resource}
        self.src_graph = BlockVersionGraph()  # BlockVersionGraph
        self.dep_graph = BlockVersionGraph()  # BlockVersionGraph

    @property
    def version_graph(self):
        return self.src_graph + self.dep_graph

    SERIAL_DEP_TABLE = 'd'
    SERIAL_REFERENCES = 'r'
    SERIAL_CLOSURE = 'c'
    SERIAL_SRC_GRAPH = 'sg'
    SERIAL_DEP_GRAPH = 'dg'

    def serialize(self):
        return Serializer().build(
            (HiveDependencies.SERIAL_DEP_TABLE, self.dep_table),
            (HiveDependencies.SERIAL_REFERENCES, self.references),
            (HiveDependencies.SERIAL_CLOSURE, self.closure),
            (HiveDependencies.SERIAL_SRC_GRAPH, self.src_graph),
            (HiveDependencies.SERIAL_DEP_GRAPH, self.dep_graph),
        )

    @staticmethod
    def deserialize(data):
        try:
            res = HiveDependencies()
            res.dep_table = BlockVersionTable.deserialize(data[HiveDependencies.SERIAL_DEP_TABLE])
            res.references = References.deserialize(data[HiveDependencies.SERIAL_REFERENCES])
            res.closure = Closure.deserialize(data[HiveDependencies.SERIAL_CLOSURE])
            res.src_graph = BlockVersionGraph.deserialize(data[HiveDependencies.SERIAL_SRC_GRAPH])
            res.dep_graph = BlockVersionGraph.deserialize(data[HiveDependencies.SERIAL_DEP_GRAPH])
            return res
        except Exception as e:
            raise BiiSerializationException(e)
