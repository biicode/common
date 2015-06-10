import unittest

from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.cells import Cell
from biicode.common.model.resource import Resource
from biicode.common.deps.closure import Closure, ClosureItem
from biicode.common.output_stream import OutputStream
from biicode.common.edition.bii_config import BiiConfig, template
from biicode.common.model.content import Content
from biicode.common.model.blob import Blob
from biicode.common.edition.block_holder import BIICODE_FILE


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

    def test_bii_config_deps(self):
        c1 = Closure()
        biiout = OutputStream()

        bii_conf_1 = 'user/block1/%s' % BIICODE_FILE
        r1 = Resource(Cell(bii_conf_1), Content(bii_conf_1, load=Blob(template)))
        r2 = Resource(Cell('user/block1/my_cell.c'), None)
        version_1 = BlockVersion(BRLBlock('owner/user/block1/branch'), 4)
        c1.add_item(r1, version_1, biiout)
        c1.add_item(r2, version_1, biiout)

        bii_conf_2 = 'user/block2/%s' % BIICODE_FILE
        r3 = Resource(Cell(bii_conf_2), Content(bii_conf_2, load=Blob(template)))
        r4 = Resource(Cell('user/block2/my_cell.c'), None)
        version_2 = BlockVersion(BRLBlock('owner/user/block2/branch'), 2)
        c1.add_item(r3, version_2, biiout)
        c1.add_item(r4, version_2, biiout)

        all_bii_configs = c1.bii_config()
        bii_config_content = BiiConfig(template).dumps()
        self.assertEqual(all_bii_configs.keys(), ['user/block2', 'user/block1'])
        self.assertEqual(all_bii_configs['user/block1'].dumps(), bii_config_content)
        self.assertEqual(all_bii_configs['user/block2'].dumps(), bii_config_content)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
