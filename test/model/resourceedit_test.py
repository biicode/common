import unittest
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.cells import SimpleCell
from biicode.common.model.bii_type import UNKNOWN


class CellEditTest(unittest.TestCase):
    def test_cell(self):
        brl = BlockCellName("drodri/pang/test.cpp")
        r = SimpleCell(brl)

        self.assertFalse(r.hasMain)
        self.assertEquals(r.name, brl)
        self.assertEquals(r.type, UNKNOWN)
