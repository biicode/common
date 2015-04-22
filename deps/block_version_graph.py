from biicode.common.deps.directed_graph import DirectedGraph
from collections import defaultdict


class BlockVersionGraph(DirectedGraph):
    '''Graph of dependencies of published things with Nodes=BlockVersions'''

    @property
    def versions(self):
        '''return all versions for all blocknames in a dictionary
        '''
        result = defaultdict(set)
        for node in self.nodes:
            result[node.block_name].add(node)
        return result

    def collision(self, other):
        '''computation of the minimum graph that contains possible sources of incompatibilities
        param other: another BlockVersionGraph to compute the intersection with self
        return: a new BlockVersionGraph'''
        graph_union = self + other
        versions = graph_union.versions
        conflictive = []
        for vers in versions.itervalues():
            if len(vers) > 1:
                conflictive.extend(vers)
        result = BlockVersionGraph()
        for c in conflictive:
            closure = graph_union.inverse_reachable_subgraph(c)
            result += closure
            #FIXME: missing edges in this result
        return result

    def sanitize(self, response):
        """ this method removes those edges that are not supported (target) by a node. This can
        happen if a graph is incomplete, maybe because a block has been deleted or permissions
        have been restricted and user has no access
        """
        nodes = self.nodes
        invalid_edges = []
        for edge in self.edges:
            if edge.target not in nodes:
                response.error('Requirement "%s" not found' % str(edge.target))
                invalid_edges.append(edge)
        self.edges.difference_update(invalid_edges)
