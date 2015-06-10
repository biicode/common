from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.deps.closure import Closure


class ProjectDependencies(object):
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

    @property
    def bii_config(self):
        ''' Return a dict of biicode.conf objects, e.g.:
                {user/superblock: <bii_config_object>,
                user_2/otherblock: <bii_config_object>}
        '''
        return self.closure.bii_config()
