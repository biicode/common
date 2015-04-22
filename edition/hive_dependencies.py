from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.deps.closure import Closure


class HiveDependencies(object):
    """ This is a caching object for storing the block and version level dependencies of the
    current graph, as well as the closure
    """
    def __init__(self):
        self.references = None  # References()
        self.closure = Closure()  # {BlockCellName: Resource}
        self.src_graph = BlockVersionGraph()  # BlockVersionGraph
        self.dep_graph = BlockVersionGraph()  # BlockVersionGraph

    @property
    def version_graph(self):
        return self.src_graph + self.dep_graph
