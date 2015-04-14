import unittest
from biicode.common.model.declare.data_declaration import DataDeclaration
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.brl.block_name import BlockName
from biicode.common.exception import BiiException


class DataDeclarationTest(unittest.TestCase):

    def setUp(self):
        self.sut = DataDeclaration("user/wizard/math/matrix.h")

    def eq_test(self):
        self.assertTrue(self.sut == self.sut)

    def eq_false_test(self):
        self.assertFalse(self.sut == 1)

    def exact_match_test(self):
        block_cell_name = BlockCellName("user/wizard/math/matrix.h")
        blocks = [block_cell_name]
        self.assertEquals(self.sut.match(blocks), set([block_cell_name]))

    def partial_match_test(self):
        block_cell_name = BlockCellName("user/wizard/math/matrix.h")
        blocks = [block_cell_name]
        self.assertEquals(self.sut.match(blocks, block_cell_name), set([block_cell_name]))

    def negative_match_test(self):
        sut = DataDeclaration("user/wizard/math/scene.h")
        block_cell_name = BlockCellName("user/wizard/math/matrix.h")
        blocks = [block_cell_name]
        self.assertEquals(sut.match(blocks, block_cell_name), set([]))

    def block_test(self):
        self.assertEquals(self.sut.block(), BlockName("user/wizard"))

    def normalize_test_raises_exception(self):
        self.assertRaises(BiiException, self.sut.normalize, ["a", "b"])

    def normalize_test_return_same_data_declaration(self):
        self.assertEquals(self.sut.normalize([BlockCellName('user\\wizard\\math\\matrix.h')]), self.sut)
