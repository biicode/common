import unittest

from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.brl.cell_name import CellName
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.symbolic.reference import Reference, References
import copy


class ReferenceTest(unittest.TestCase):

    def test_name(self):
        m = BRLBlock('owner/user/block/branch')
        mv = BlockVersion(m, 3)
        r = Reference(mv, CellName('path/to/file.h'))
        self.assertEqual('user/block/path/to/file.h', r.block_cell_name())

    def test_deepcopy(self):
        r = References()
        r[BlockVersion(BRLBlock('user/user/block/branch'), 3)].add(CellName('f1.h'))
        r2 = copy.deepcopy(r)
        self.assertEqual(r, r2)

    def test_references(self):
        r = References()
        bv3 = BlockVersion(BRLBlock('user/user/block/master'), 3)
        bv4 = BlockVersion(BRLBlock('user/user/block/master'), 4)
        cn0 = CellName('foo.h')
        cn1 = CellName('foo1.h')
        r[bv3].add(cn0)
        r[bv3].add(cn1)
        r[bv4].add(cn0)
        l = r.explode()
        self.assertEqual({(bv3, cn0), (bv3, cn1), (bv4, cn0)}, set(l))
        # r.discard(Reference(bv4, cn0))
        # l=r.explode()
        # self.assertEqual({(bv3,cn0), (bv3,cn1)},set(l))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
