import unittest
from biicode.common.model.block_delta import BlockDelta
import time
from biicode.common.model.version_tag import ALPHA, DEV, STABLE


class BlockDeltaTest(unittest.TestCase):

    def test_block_delta(self):
        t = BlockDelta("hola mensajito", ALPHA, time.time(), commiter="User1")
        s = t.serialize()
        t2 = BlockDelta.deserialize(s)
        self.assertEqual(t, t2)

    def test_equals(self):
        block_delta = BlockDelta("seven horses in bonanza", DEV, 2, commiter="User1")
        block_delta2 = BlockDelta("eight horses in bonanza", DEV, 2, commiter="User4")

        self.assertNotEquals(block_delta, block_delta2)
        self.assertNotEquals(block_delta.commiter, block_delta2.commiter)

        block_delta2.msg = block_delta.msg
        block_delta2.commiter = block_delta.commiter
        self.assertEquals(block_delta, block_delta2)

        block_delta2.date = 1
        self.assertNotEquals(block_delta, block_delta2)

        block_delta2.date = 2
        block_delta2.tag = STABLE
        self.assertNotEquals(block_delta, block_delta2)

        block_delta.tag = STABLE
        self.assertEqual(str(block_delta), str(block_delta))

    def test_serialize(self):
        block_delta = BlockDelta("seven horses in bonanza", STABLE, 2, commiter="User1")
        s = block_delta.serialize()
        self.assertEquals(block_delta, BlockDelta.deserialize(s))

        block_delta = BlockDelta("seven horses in bonanza", STABLE, 2, 'mytag', commiter="User1")
        s = block_delta.serialize()
        self.assertEquals(block_delta, BlockDelta.deserialize(s))
