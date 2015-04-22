from pygraph.classes.digraph import digraph
from pygraph.algorithms.sorting import topological_sorting
from pygraph.algorithms.cycles import find_cycle
from collections import namedtuple


class Edge(namedtuple('Edge', ['source', 'target', 'value'])):
    pass


class DirectedGraph(object):
    '''Graph that allows multiple edges between two nodes'''

    def __init__(self):
        self._cached_graph = None
        self.edges = set()
        self.nodes = set()

    def __add__(self, other):
        '''Returns an object of the same type as self'''
        result = self.__class__()
        result.nodes.update(self.nodes)
        result.edges.update(self.edges)
        if other:
            result.nodes.update(other.nodes)
            result.edges.update(other.edges)
        return result

    def __iadd__(self, other):
        '''Returns an object of the same type as self'''
        if other:
            self.nodes.update(other.nodes)
            self.edges.update(other.edges)
        return self

    def __nonzero__(self):
        return len(self.nodes) > 0

    def add_edge(self, source, target, value=None):
        self.edges.add(Edge(source, target, value))
        self._cached_graph = None

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.add(node)
            self._cached_graph = None

    def delete_node(self, node):
        self.nodes.discard(node)
        remove = [edge for edge in self.edges if edge.source == node or edge.target == node]
        self.edges.difference_update(remove)
        self._cached_graph = None

    def nodes_edges(self, source_node, target_node):
        '''return all edges between two nodes'''
        return [x for x in self.edges if (x.source, x.target) == (source_node, target_node)]

    def incoming_edges(self, node):
        '''Return all edges that have node as target'''
        return [x for x in self.edges if x.target == node]

    def neighbours(self, node):
        '''return all neighbor nodes navigable from node'''
        return [x.target for x in self.edges if x.source == node]

    def neighbours_to(self, node):
        '''return all neighbor nodes to the node-INEFFICIENCY'''
        return [x.source for x in self.edges if x.target == node]

    @property
    def _graph(self):
        if self._cached_graph is None:
            self._cached_graph = digraph()
            self._cached_graph.add_nodes(self.nodes)
            for edge in self.edges:
                source = edge.source
                target = edge.target
                # accounts for our multi-edge approach
                if (not self._cached_graph.has_edge((source, target)) and source in self.nodes and
                    target in self.nodes):
                    self._cached_graph.add_edge((source, target))
        return self._cached_graph

    def get_cycles(self):
        '''computes one cycle or an empty list'''
        # FIXME: check complexity
        return find_cycle(self._graph)

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) and \
            self.nodes == other.nodes and self.edges == other.edges

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        result = []
        result.append(repr(self.nodes))
        for edge in self.edges:
            result.append(repr(edge))
        return '\n'.join(result)

    def get_levels(self):
        '''arrange the nodes in layers according to degree
        level 0 will have no outgoing edges, last level will have no incoming edges'''
        # Topological order: any strict order which satisfies the partial order
        # as established by the outgoing edges
        graph = self._graph
        ordered = topological_sorting(graph)
        ordered.reverse()
        # print 'ordered %s'%ordered
        result = []
        for elem in ordered:
            deps = graph.neighbors(elem)
            maximo = -1
            for i, level in enumerate(result):
                for d in deps:
                    if d in level and i > maximo:
                        maximo = i

            if maximo + 1 >= len(result):
                result.append(set())
            result[maximo + 1].add(elem)

        return result

    def get_paths(self, node):
        '''Paths from root to node'''
        edges = self.incoming_edges(node)
        if not edges:
            return [[node]]
        else:
            result = []
            for edge in edges:
                paths = self.get_paths(edge.source)
                for path in paths:
                    path.append(node)
                    result.append(path)
            return result

    def compute_closure(self, node):
        '''transitive closure of (FROM) the node, excluding the node'''
        graph = self._graph
        result = set()
        open_set = set(graph.neighbors(node))
        while open_set:
            elem = open_set.pop()
            result.add(elem)
            neigh = set(graph.neighbors(elem))
            open_set.update(neigh.difference(result))
        return result

    def inverse_reachable_subgraph(self, node):
        '''subgraph containing all nodes with reachability TO node, or the one that might
        result from the direct reachability with all edges inversed'''

        # Does not build the digraph: potentially inefficient
        result = self.__class__()
        open_set = {node}        # inefficiency issue
        result.add_node(node)
        while open_set:
            elem = open_set.pop()

            neigh = set(self.neighbours_to(elem))       # inefficiency issue
            new_nodes = neigh.difference(result.nodes)
            open_set.update(new_nodes)
            result.add_nodes(new_nodes)

            add_edges_nodes = neigh.intersection(result.nodes)
            for n in add_edges_nodes:
                result.add_edge(n, elem)
        return result
