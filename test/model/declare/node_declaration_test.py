from unittest import TestCase
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.node_declaration import NodeDeclaration
from nose.plugins.attrib import attr


@attr('node')
class TestNodeDeclaration(TestCase):

    def test_usual_node_import(self):
        cut = NodeDeclaration("fran/noderedis")
        self.assertEquals("fran/noderedis", cut.block())

    def test_metrics_require(self):
        cut = NodeDeclaration("metrics")
        self.assertEquals(None, cut.block())

    def test_path_rel_require(self):
        cut = NodeDeclaration("./")
        self.assertEquals(None, cut.block())

    def test_extension_namelist(self):
        cut = NodeDeclaration("fran/noderedis/index")
        self.assertItemsEqual(["fran/noderedis/index.json",
                               "fran/noderedis/index.js",
                               "fran/noderedis/index.node"], cut._extension_name)

    def test_extension_namelist_with_relative(self):
        cut = NodeDeclaration(".lib/queue")
        cut.extension_namelist()
        self.assertItemsEqual([".lib/queue.json",
                               ".lib/queue.js",
                               ".lib/queue.node"], cut._extension_name)

    def test_extension_namelist_with_extension(self):
        cut = NodeDeclaration("fran/noderedis/index.js")
        cut.extension_namelist()
        self.assertItemsEqual(["fran/noderedis/index.js"], cut._extension_name)

    def test_explicit_node_require(self):
        cut = NodeDeclaration("fran/noderedis/index.js")
        self.assertEquals("fran/noderedis", cut.block())
        self.assertEquals(BlockCellName("fran/noderedis/index.js"), cut.block_cell_name())

    def test_relative_require(self):
        cut = NodeDeclaration("../parser")
        origin_block_cell_name = BlockCellName("fran/noderedis/other/other.js")

        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/other/other.js"),
                            BlockCellName("fran/noderedis/parser.js")]

        self.assertItemsEqual(set(["fran/noderedis/parser.js"]),
                              cut.match(block_cell_names, origin_block_cell_name))

    def test_relative_require_not_found(self):
        cut = NodeDeclaration("../parser")
        origin_block_cell_name = BlockCellName("fran/noderedis/other/thing/other.js")

        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/other/thing/other.js"),
                            BlockCellName("fran/noderedis/parser.js")]

        self.assertItemsEqual(set(), cut.match(block_cell_names, origin_block_cell_name))

    def test_one_level_relative_require(self):
        cut = NodeDeclaration("./lib/queue")
        origin_block_cell_name = BlockCellName("fran/noderedis/index.js")

        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/lib/queue.js"),
                            BlockCellName("fran/noderedis/lib/parser.js")]

        self.assertItemsEqual(set(["fran/noderedis/lib/queue.js"]),
                              cut.match(block_cell_names, origin_block_cell_name))

    def test_one_level_relative_require_with_depth(self):
        cut = NodeDeclaration("./lib/parser/queue")
        origin_block_cell_name = BlockCellName("fran/noderedis/index.js")

        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/lib/queue.js"),
                            BlockCellName("fran/noderedis/lib/parser/queue.js")]

        self.assertItemsEqual(set(["fran/noderedis/lib/parser/queue.js"]),
                              cut.match(block_cell_names, origin_block_cell_name))

    def test_match_with_implicit_require(self):
        cut = NodeDeclaration("fran/noderedis")

        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/other.js")]

        self.assertItemsEqual(set([BlockCellName("fran/noderedis/index.js")]),
                              cut.match(block_cell_names))

    def test_match_with_implicit_require_with_index_and_package(self):
        cut = NodeDeclaration("fran/noderedis")

        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/package.json"),
                            BlockCellName("fran/noderedis/other.js")]
        self.assertItemsEqual(set([BlockCellName("fran/noderedis/index.js"),
                              BlockCellName("fran/noderedis/package.json")]),
                              cut.match(block_cell_names))

    def test_match_with_implicit_require_nothing_found(self):
        cut = NodeDeclaration("fran/noderedis")
        block_cell_names = [BlockCellName("fran/noderedis/other.js")]
        self.assertItemsEqual(set(), cut.match(block_cell_names))

    def test_same_path_relative_index_require(self):
        cut = NodeDeclaration("./")
        origin_block_cell_name = BlockCellName("fran/noderedis/bench.js")
        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/client.js")]

        m = cut.match(block_cell_names, origin_block_cell_name)
        self.assertItemsEqual(set(["fran/noderedis/index.js"]), m)

    def test_package_json_recognition(self):
        cut = NodeDeclaration("fran/noderedis")

        block_cell_names = [BlockCellName("fran/noderedis/package.json"),
                            BlockCellName("fran/noderedis/other.js")]

        self.assertItemsEqual(set([BlockCellName("fran/noderedis/package.json")]),
                              cut.match(block_cell_names))

    def test_normalize_declaration(self):
        cut = NodeDeclaration("fran/noderedis")
        block_cell_names = [BlockCellName("fran/noderedis/package.json")]
        self.assertEquals(cut, cut.normalize(block_cell_names))

    def test_normalize_declaration_package_and_index(self):
        cut = NodeDeclaration("fran/noderedis")
        block_cell_names = [BlockCellName("fran/noderedis/index.js"),
                            BlockCellName("fran/noderedis/package.json")]
        self.assertEquals(cut, cut.normalize(block_cell_names))
