import unittest

from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.cells import Cell
from biicode.common.model.resource import Resource
from biicode.common.deps.closure import Closure, ClosureItem
from biicode.common.output_stream import OutputStream


class ClosureTest(unittest.TestCase):

    def test_add_item(self):
        c1 = Closure()
        r1 = Cell('user/block/name1')
        version = BlockVersion(BRLBlock('owner/user/block/branch'), 13)
        biiout = OutputStream()
        resource = Resource(r1, None)
        c1.add_item(resource, version, biiout)
        r2 = Cell('user/block/name1')
        r2.hasMain = True
        resource2 = Resource(r2, None)
        version2 = BlockVersion(BRLBlock('owner/user/block/branch'), 14)
        c1.add_item(resource2, version2, biiout)

        self.assertEqual(ClosureItem(resource, version), c1['user/block/name1'])
        self.assertIn('Incompatible dependency', str(biiout))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
