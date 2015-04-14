import unittest
from biicode.common.model.block_info import BlockInfo
from biicode.common.model.symbolic.block_version import BlockVersion


class BlockInfoTest(unittest.TestCase):

    def test_block_info(self):
        bversion = BlockVersion("phil/phil/super_block/master", "0")
        t = BlockInfo(True, bversion, False)
        s = t.serialize()
        t2 = BlockInfo.deserialize(s)
        self.assertEqual(t, t2)

    def test_equals(self):
        bversion = BlockVersion("phil/phil/super_block/master", "0")
        bversion2 = BlockVersion("fenix/fenix/slight_block/master", "0")

        block_info = BlockInfo(True, bversion, False)
        block_info2 = BlockInfo(True, bversion, False)

        self.assertEquals(block_info, block_info2)

        block_info2.last_version = bversion2
        self.assertNotEquals(block_info, block_info2)

        block_info2.last_version = bversion
        block_info.can_write = False
        self.assertNotEquals(block_info, block_info2)

        block_info.can_write = True
        block_info.private = True
        self.assertNotEquals(block_info, block_info2)
