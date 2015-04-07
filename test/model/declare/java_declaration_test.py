from unittest import TestCase
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.java_declaration import JavaDeclaration


class JavaDeclarationTest(TestCase):

    def test_from_import_block(self):
        sut = JavaDeclaration("biicode.common.edition.Parser")
        self.assertEquals("biicode/common", sut.block())

    def test_general_import_block(self):
        sut = JavaDeclaration("biicode.common.edition")
        self.assertEquals("biicode/common", sut.block())

    def test_simple_match(self):
        sut = JavaDeclaration("biicode.common.Edition")
        block_cell_names = set([BlockCellName("biicode/common/Edition.java"),
                                BlockCellName("biicode/common/Jarl.java")])
        self.assertEquals(set([BlockCellName("biicode/common/Edition.java")]),
                          sut.match(block_cell_names))

    def test_normalize(self):
        sut = JavaDeclaration("myblock")
        result = sut.normalize(['testuser/block/Myblock.java'])
        self.assertEquals(JavaDeclaration("testuser.block.Myblock"), result)

    def test_normalize_composed_import(self):
        sut = JavaDeclaration("biicode.common.edition.Parsing")
        result = sut.normalize(['biicode/common/edition/Parsing.java'])
        self.assertEquals(JavaDeclaration("biicode.common.edition.Parsing"), result)
