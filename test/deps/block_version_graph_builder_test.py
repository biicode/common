import unittest

from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.deps.block_version_graph_builder import \
    compute_effective, block_version_graph_build
from biicode.common.test.deps.deps_api import DepsApiFake
from biicode.common.model.symbolic.block_version_table import BlockVersionTable


a1 = BlockVersion.loads('user0/blocka: 1')
a2 = BlockVersion.loads('user0/blocka: 2')
an = BlockVersion.loads('user0/blocka')
b1 = BlockVersion.loads('user0/blockb: 1')
b2 = BlockVersion.loads('user0/blockb: 2')
bn = BlockVersion.loads('user0/blockb')
c1 = BlockVersion.loads('user0/blockc: 1')
c2 = BlockVersion.loads('user0/blockc: 1')
c3 = BlockVersion.loads('user0/blockc: 3')
cn = BlockVersion.loads('user0/blockc')
d1 = BlockVersion.loads('user0/blockd: 1')


class BlockVersionGraphBuilderTest(unittest.TestCase):

    def test_compose(self):
        t1 = BlockVersionTable([a1])
        t2 = BlockVersionTable([b1])
        effective, propagate, overwrites = compute_effective(t1, t2, 'user0/blocka')
        self.assertEqual(effective, BlockVersionTable([b1]))
        self.assertEqual(propagate, BlockVersionTable([b1]))
        self.assertEqual(set(), overwrites)

        t1 = BlockVersionTable([a1, c1])
        t2 = BlockVersionTable([b1])
        effective, propagate, overwrites = compute_effective(t1, t2, 'user0/blocka')
        self.assertEqual(effective, BlockVersionTable([b1]))
        self.assertEqual(propagate, BlockVersionTable([b1, c1]))
        self.assertEqual(set(), overwrites)

        t1 = BlockVersionTable([a1, b2])
        t2 = BlockVersionTable([b1])
        effective, propagate, overwrites = compute_effective(t1, t2, 'user0/blocka')
        self.assertEqual(effective, BlockVersionTable([b2]))
        self.assertEqual(propagate, BlockVersionTable([b2]))
        self.assertEqual({b2}, overwrites)

    def test_one_level(self):
        base_versions = [a1]
        api = DepsApiFake({a1: [b1],
                           b1: []})
        graph, overwrites = block_version_graph_build(api.get_dep_table, base_versions, {})

        expected = BlockVersionGraph()
        expected.add_nodes([a1, b1])
        expected.add_edge(a1, b1)
        self.assertEqual(graph, expected)

    def test_two_levels(self):
        base_versions = [a1]
        api = DepsApiFake({a1: [b1],
                           b1: [c1, d1],
                           c1: [], d1: []})
        graph, overwrites = block_version_graph_build(api.get_dep_table, base_versions, {})

        expected = BlockVersionGraph()
        expected.add_nodes([a1, b1, c1, d1])
        expected.add_edge(a1, b1)
        expected.add_edge(b1, c1)
        expected.add_edge(b1, d1)
        self.assertEqual(graph, expected)

    def test_diamond(self):
        base_versions = [a1, b1]
        api = DepsApiFake({a1: [c1],
                           b1: [c1],
                           c1: []})
        graph, overwrites = block_version_graph_build(api.get_dep_table, base_versions, {})

        expected = BlockVersionGraph()
        expected.add_nodes([a1, b1, c1])
        expected.add_edge(a1, c1)
        expected.add_edge(b1, c1)
        self.assertEqual(graph, expected)
        self.assertEqual({}, overwrites)

    def test_diamond_2_version(self):
        base_versions = [a1, b1]
        api = DepsApiFake({a1: [c1],
                           b1: [c2],
                           c1: [], c2: []})
        graph, overwrites = block_version_graph_build(api.get_dep_table, base_versions, {})

        expected = BlockVersionGraph()
        expected.add_nodes([a1, b1, c1, c2])
        expected.add_edge(a1, c1)
        expected.add_edge(b1, c2)
        self.assertEqual(graph, expected)
        self.assertEqual({}, overwrites)

    def test_effective_overwrite(self):
        base_versions = [a1, b1]
        api = DepsApiFake({a1: [c1],
                           b1: [c2],
                           c1: [], c2: [], c3: []})
        graph, overwrites = block_version_graph_build(api.get_dep_table, base_versions,
                                                              BlockVersionTable([c3]))

        expected = BlockVersionGraph()
        expected.add_nodes([a1, b1, c3])
        expected.add_edge(a1, c3)
        expected.add_edge(b1, c3)
        self.assertEqual(graph, expected)
        self.assertEqual({a1: {c3}, b1: {c3}}, overwrites)

    def test_effective_overwrite_none(self):
        base_versions = [a1, b1]
        api = DepsApiFake({a1: [c1],
                           b1: [c2],
                           cn: []})
        graph, overwrites = block_version_graph_build(api.get_dep_table, base_versions,
                                                              BlockVersionTable([cn]))

        expected = BlockVersionGraph()
        expected.add_nodes([a1, b1, cn])
        expected.add_edge(a1, cn)
        expected.add_edge(b1, cn)
        self.assertEqual(graph, expected)
        self.assertEqual({a1: {cn}, b1: {cn}}, overwrites)

    def test_same_tables(self):
        base_versions = [c1, d1]
        api = DepsApiFake({c1: [a2],
                           d1: [b2]})
        graph, overwrites = block_version_graph_build(api.get_dep_table, base_versions,
                                                      BlockVersionTable([an, bn, c1, d1]))
        expected = BlockVersionGraph()
        expected.add_nodes([c1, d1])
        expected.add_edge(c1, an)
        expected.add_edge(d1, bn)

        self.assertEqual(graph, expected)
        self.assertEqual({c1: {an}, d1: {bn}}, overwrites)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
