import unittest
from biicode.common.deps.directed_graph import DirectedGraph
from biicode.common.model.brl.block_name import BlockName


class DirectedGraphTest(unittest.TestCase):

    def testLevels(self):
        gr = DirectedGraph()
        gr.add_nodes([1, 2, 3, 11, 12, 21, 22, 23, 31])

        gr.add_edge(11, 1)
        gr.add_edge(12, 2)
        gr.add_edge(21, 12)
        gr.add_edge(22, 11)
        gr.add_edge(31, 21)
        gr.add_edge(31, 22)
        gr.add_edge(31, 23)

        self.assertEqual(set([1, 2, 3, 23]), gr.get_levels()[0])
        self.assertEqual(set([11, 12]), gr.get_levels()[1])
        self.assertEqual(set([22, 21]), gr.get_levels()[2])
        self.assertEqual(set([31]), gr.get_levels()[3])

        # cycles no
        self.assertEqual([], gr.get_cycles())

        self.assertEqual(set([1, 2, 11, 12, 21, 22, 23]), gr.compute_closure(31))
        self.assertEqual(set([]), gr.compute_closure(23))
        self.assertEqual(set([1, 11]), gr.compute_closure(22))
        self.assertEqual(set([2, 12]), gr.compute_closure(21))
        self.assertEqual(set([1]), gr.compute_closure(11))

        # svg=gr.getSVG()
        # f=open('file.svg','w')
        # f.write(svg)
        # webbrowser.get().open('file.svg')

    def test_get_paths(self):
        gr = DirectedGraph()
        gr.add_nodes([1, 2, 11, 12, 21, 22, 31])

        gr.add_edge(11, 1)
        gr.add_edge(12, 2)
        gr.add_edge(21, 12)
        gr.add_edge(22, 11)
        gr.add_edge(22, 12)
        gr.add_edge(31, 21)
        gr.add_edge(31, 22)

        paths = gr.get_paths(2)
        self.assertEqual(len(paths), 2)
        self.assertIn([31, 21, 12, 2], paths)
        self.assertIn([31, 22, 12, 2], paths)

        self.assertEqual([[31]], gr.get_paths(31))

    def testCycles(self):
        gr = DirectedGraph()
        gr.add_nodes([1, 2, 3, 11, 12, 21, 22, 23, 31])

        self.assertEqual([], gr.get_cycles())
        gr.add_edge(1, 2)
        gr.add_edge(2, 3)
        gr.add_edge(3, 1)

        self.assertEqual([1, 2, 3], gr.get_cycles())

    def testComputeLevels(self):
        g = DirectedGraph()
        for i in range(13):
            g.add_node(BlockName("user/mod%d" % i))

        g.add_edge(BlockName("user/mod0"), BlockName("user/mod2"))
        g.add_edge(BlockName("user/mod0"), BlockName("user/mod3"))
        g.add_edge(BlockName("user/mod0"), BlockName("user/mod4"))
        g.add_edge(BlockName("user/mod3"), BlockName("user/mod6"))
        g.add_edge(BlockName("user/mod4"), BlockName("user/mod7"))
        g.add_edge(BlockName("user/mod6"), BlockName("user/mod9"))
        g.add_edge(BlockName("user/mod7"), BlockName("user/mod9"))
        g.add_edge(BlockName("user/mod9"), BlockName("user/mod12"))

        g.add_edge(BlockName("user/mod1"), BlockName("user/mod5"))
        g.add_edge(BlockName("user/mod5"), BlockName("user/mod8"))
        g.add_edge(BlockName("user/mod8"), BlockName("user/mod10"))
        g.add_edge(BlockName("user/mod8"), BlockName("user/mod11"))

        g.add_edge(BlockName("user/mod10"), BlockName("user/mod12"))
        g.add_edge(BlockName("user/mod7"), BlockName("user/mod10"))

        result = g.get_levels()

        self.assertEquals(5, len(result))
        self.assertEquals(result[0], set([BlockName("user/mod12"),
                                          BlockName("user/mod11"),
                                          BlockName("user/mod2")
                                          ]))

        self.assertEquals(result[1], set([BlockName("user/mod9"),
                                          BlockName("user/mod10")]))

        self.assertEquals(result[2], set([BlockName("user/mod6"),
                                          BlockName("user/mod7"),
                                          BlockName("user/mod8")]))

        self.assertEquals(result[3], set([BlockName("user/mod3"),
                                          BlockName("user/mod4"),
                                          BlockName("user/mod5")]))

        self.assertEquals(result[4], set([BlockName("user/mod0"),
                                          BlockName("user/mod1")]))

    def testCycles2(self):
        g = DirectedGraph()
        for i in range(2):
            g.add_node(BlockName("user/mod%d" % i))

        g.add_edge(BlockName("user/mod0"), BlockName("user/mod1"))
        g.add_edge(BlockName("user/mod1"), BlockName("user/mod0"))
        self.assertEqual({BlockName("user/mod0"), BlockName("user/mod1")}, set(g.get_cycles()))

    def test_closures(self):
        gr = DirectedGraph()
        gr.add_nodes([1, 2, 3, 11, 12, 21, 22, 23, 31])

        gr.add_edge(11, 1)
        gr.add_edge(12, 2)
        gr.add_edge(21, 12)
        gr.add_edge(22, 11)
        gr.add_edge(31, 21)
        gr.add_edge(31, 22)
        gr.add_edge(31, 23)

        self.assertEqual({21, 12, 2, 22, 11, 1, 23}, set(gr.compute_closure(31)))
        # Inverse closure
        self.assertEqual({31}, gr.inverse_reachable_subgraph(31).nodes)
        self.assertEqual({11, 22, 31, 1}, gr.inverse_reachable_subgraph(1).nodes)
