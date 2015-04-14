import unittest
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.deps.block_version_graph import BlockVersionGraph


class BlockVersionGraphTest(unittest.TestCase):

    def empty_test(self):
        '''When one is empty, it should always be compatible'''
        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()
        self.assertFalse(g1.collision(g2))

        brl0 = BRLBlock('user/user/block/master')
        brl1 = BRLBlock('user/user/block2/master')
        v0 = BlockVersion(brl0, 0)
        v1 = BlockVersion(brl1, 1)
        g1.add_node(v0)
        self.assertFalse(g1.collision(g2))
        self.assertFalse(g2.collision(g1))

        g1.add_node(v1)
        self.assertFalse(g1.collision(g2))
        self.assertFalse(g2.collision(g1))

    def compatible_test(self):
        '''both not empty, but compatible'''
        brl0 = BRLBlock('user/user/block/master')
        brl1 = BRLBlock('user/user/block2/master')
        v0 = BlockVersion(brl0, 0)
        v1 = BlockVersion(brl1, 1)

        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()
        g1.add_node(v0)
        g2.add_node(v1)
        self.assertFalse(g1.collision(g2))
        self.assertFalse(g2.collision(g1))

        g1.add_node(v1)
        g2.add_node(v0)
        self.assertFalse(g1.collision(g2))
        self.assertFalse(g2.collision(g1))

    def incompatible_test(self):
        '''both not empty, and incompatible'''
        brl0 = BRLBlock('user/user/block/master')
        brl1 = BRLBlock('user/user/block2/master')
        v0 = BlockVersion(brl0, 0)
        v1 = BlockVersion(brl1, 1)
        v2 = BlockVersion(brl1, 0)
        v3 = BlockVersion(brl0, 1)

        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()
        g1.add_node(v0)
        g2.add_node(v3)
        self.assertTrue(g1.collision(g2))
        self.assertTrue(g2.collision(g1))

        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()
        g1.add_nodes([v0, v1])
        g2.add_nodes([v2, v3])
        self.assertTrue(g1.collision(g2))
        self.assertTrue(g2.collision(g1))

    def disjoints_graphs_no_collisions_test(self):
        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()
        self.assertEqual(BlockVersionGraph(), g1.collision(g2))
        self.assertEqual(BlockVersionGraph(), g2.collision(g1))

        brl0 = BRLBlock('user/user/block/master')
        brl1 = BRLBlock('user/user/block2/master')
        v0 = BlockVersion(brl0, 0)
        v1 = BlockVersion(brl1, 1)

        g1.add_node(v0)
        g2.add_node(v1)
        self.assertEqual(BlockVersionGraph(), g1.collision(g2))
        self.assertEqual(BlockVersionGraph(), g2.collision(g1))

    def connected_graphs_no_collisions_test(self):
        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()

        brl0 = BRLBlock('user/user/block/master')
        brl1 = BRLBlock('user/user/block2/master')
        v0 = BlockVersion(brl0, 0)
        v1 = BlockVersion(brl1, 1)

        g1.add_node(v0)
        g2.add_node(v0)
        self.assertEqual(BlockVersionGraph(), g1.collision(g2))
        self.assertEqual(BlockVersionGraph(), g2.collision(g1))
        g1.add_node(v1)
        self.assertEqual(BlockVersionGraph(), g1.collision(g2))
        self.assertEqual(BlockVersionGraph(), g2.collision(g1))

    def simple_collisions_test(self):
        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()

        brl0 = BRLBlock('user/user/block/master')
        v0 = BlockVersion(brl0, 0)
        v1 = BlockVersion(brl0, 1)

        g1.add_node(v0)
        g2.add_node(v1)
        expected = BlockVersionGraph()
        expected.add_nodes([v0, v1])
        self.assertEqual(expected, g1.collision(g2))
        self.assertEqual(expected, g2.collision(g1))

    def diamond_collisions_test(self):
        g1 = BlockVersionGraph()
        g2 = BlockVersionGraph()

        brlA = BRLBlock('user/user/blockA/master')
        brlB = BRLBlock('user/user/blockB/master')
        brlC = BRLBlock('user/user/blockC/master')
        brlD = BRLBlock('user/user/blockD/master')
        brlE = BRLBlock('user/user/blockE/master')
        brlF = BRLBlock('user/user/blockF/master')
        vA0 = BlockVersion(brlA, 0)
        vA1 = BlockVersion(brlA, 1)
        vB = BlockVersion(brlB, 0)
        vC = BlockVersion(brlC, 1)
        vD = BlockVersion(brlD, 0)
        vE = BlockVersion(brlE, 3)
        vF = BlockVersion(brlF, 13)

        g1.add_nodes([vA0, vB, vD, vF, vE])
        g1.add_edge(vB, vA0)
        g1.add_edge(vD, vB)
        g1.add_edge(vA0, vE)

        g2.add_nodes([vA1, vC, vD, vE])
        g2.add_edge(vC, vA1)
        g2.add_edge(vD, vC)
        g2.add_edge(vA1, vE)

        expected = BlockVersionGraph()
        expected.add_nodes([vA0, vA1, vB, vC, vD])
        expected.add_edge(vC, vA1)
        expected.add_edge(vD, vC)
        expected.add_edge(vD, vB)
        expected.add_edge(vB, vA0)
        self.assertEqual(expected, g1.collision(g2))
        self.assertEqual(expected, g2.collision(g1))


