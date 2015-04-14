import unittest
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.exception import BiiException
from biicode.common.model.brl.block_cell_name import BlockCellName


class CPPDeclarationTest(unittest.TestCase):

    def testBasic(self):
        d = CPPDeclaration("sphere.h")
        d2 = CPPDeclaration("sphere.h")
        d3 = CPPDeclaration("sphere2.h")
        self.assertEquals(d, d2)
        self.assertNotEqual(d, d3)

    def testNormalizeWithWrongInput(self):
        d = CPPDeclaration("sphere.h")
        self.assertRaises(BiiException, d.normalize, ["sphere.h", "gtest.g"])

    def testNormalize(self):
        d = CPPDeclaration("sphere.h")
        d2 = CPPDeclaration("sphere2.h")
        self.assertEquals(d.normalize(["sphere.h"]), None)
        self.assertEquals(d.normalize(["sphere2.h"]), d2)

    def test_relative_match(self):
        #Given
        cut = CPPDeclaration("sphere.h")
        from_block_cell_name = BlockCellName('fran/test/main.cpp')
        block_cell_names = [BlockCellName("fran/test/sphere.h"),
                            BlockCellName("fran/test/other/jarl.cpp"),
                            BlockCellName("fran/test/main.cpp")]

        #When
        result = cut.match(block_cell_names, from_block_cell_name)

        #Then
        expected = set([BlockCellName('fran/test/sphere.h')])
        self.assertEquals(result, expected)

    def test_relative_parent_match(self):
        #Given
        cut = CPPDeclaration("../other/sphere.h")
        from_block_cell_name = BlockCellName('fran/test/main.cpp')
        block_cell_names = [BlockCellName("fran/other/sphere.h"),
                            BlockCellName("fran/test/other/jarl.cpp"),
                            BlockCellName("fran/test/main.cpp")]

        #When
        result = cut.match(block_cell_names, from_block_cell_name)

        #Then
        expected = set([BlockCellName('fran/other/sphere.h')])
        self.assertEquals(result, expected)

    def test_absolute_match(self):
        #Given
        cut = CPPDeclaration("fran/test/sphere.h")
        from_block_cell_name = BlockCellName('fran/test/main.cpp')
        block_cell_names = [BlockCellName("fran/test/sphere.h"),
                            BlockCellName("fran/test/other/jarl.cpp"),
                            BlockCellName("fran/test/main.cpp")]

        #When
        result = cut.match(block_cell_names, from_block_cell_name)

        #Then
        expected = set([BlockCellName('fran/test/sphere.h')])
        self.assertEquals(result, expected)

    def test_absolute_other_block_match(self):
        #Given
        cut = CPPDeclaration("fran/other/sphere.h")
        from_block_cell_name = BlockCellName('fran/test/main.cpp')
        block_cell_names = [BlockCellName("fran/other/sphere.h"),
                            BlockCellName("fran/test/other/jarl.cpp"),
                            BlockCellName("fran/test/main.cpp")]

        #When
        result = cut.match(block_cell_names, from_block_cell_name)

        #Then
        expected = set([BlockCellName('fran/other/sphere.h')])
        self.assertEquals(result, expected)

    def test_deps_block_match(self):
        #Given
        cut = CPPDeclaration("../../deps/akka/math/sphere.h")
        from_block_cell_name = BlockCellName('fran/test/main.cpp')
        block_cell_names = [BlockCellName("akka/math/sphere.h"),
                            BlockCellName("fran/test/other/jarl.cpp"),
                            BlockCellName("fran/test/main.cpp")]

        #When
        result = cut.match(block_cell_names, from_block_cell_name)

        #Then
        expected = set([BlockCellName('akka/math/sphere.h')])
        self.assertEquals(result, expected)

    def test_legal_deps_block_match(self):
        #Given
        cut = CPPDeclaration("deps/sphere.h")
        from_block_cell_name = BlockCellName('fran/test/main.cpp')
        block_cell_names = [BlockCellName("akka/math/sphere.h"),
                            BlockCellName("fran/test/deps/sphere.h"),
                            BlockCellName("fran/test/main.cpp")]

        #When
        result = cut.match(block_cell_names, from_block_cell_name)

        #Then
        expected = set([BlockCellName('fran/test/deps/sphere.h')])
        self.assertEquals(result, expected)

    def test_relative_composed_block_match(self):
        #Given
        cut = CPPDeclaration("algs/astar.h")
        from_block_cell_name = BlockCellName('fran/test/main.cpp')
        block_cell_names = [BlockCellName("fran/test/algs/astar.h"),
                            BlockCellName("fran/test/main.cpp")]

        #When
        result = cut.match(block_cell_names, from_block_cell_name)

        #Then
        expected = set([BlockCellName('fran/test/algs/astar.h')])
        self.assertEquals(result, expected)
