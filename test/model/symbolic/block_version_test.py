import unittest

from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.brl.cell_name import CellName
from biicode.common.model.symbolic.reference import Reference
from biicode.common.exception import BiiException


class BlockVersionTest(unittest.TestCase):

    def test_equals(self):
        brl = BRLBlock("user/user2/module/branch")
        v1 = BlockVersion(brl, 1)
        v2 = BlockVersion(brl, 2)
        self.assertNotEqual(v1, v2)
        self.assertEqual(brl, v1.block)
        self.assertEqual(1, v1.time)
        v3 = BlockVersion(brl, 2)
        self.assertEqual(v2, v3)
        v4 = BlockVersion(brl, 2, '1.2.3')
        self.assertEqual(v3, v4)

    def testCopy(self):
        brl = BRLBlock("user/user2/module/branch")
        v1 = BlockVersion(brl, 1)
        v2 = BlockVersion(brl, 1)
        self.assertEqual(v1, v2)

    def test_hasheable(self):
        brl = BRLBlock("user/user2/module/branch")
        v1 = BlockVersion(brl, 1)
        v2 = BlockVersion(brl, 2)
        v3 = BlockVersion(brl, 2)
        self.assertNotEquals(hash(v1), hash(v2))
        self.assertEquals(hash(v3), hash(v2))
        s = set()
        s.add(v1)
        s.add(v2)
        s.add(v3)
        self.assertEqual(2, len(s))

    def test_addition(self):
        sut = BlockVersion("testU/testU/math/block", 0)
        cell_name = CellName("path/to/file.h")
        ref = sut + cell_name
        self.assertEquals(ref, Reference(sut, cell_name))

    def test_loads(self):
        v1 = BlockVersion("user/user/math/master", 3)
        self.assertEqual(v1, BlockVersion.loads('user/math: 3'))
        self.assertEqual(v1, BlockVersion.loads('user/math: 3  # This is a comment'))
        self.assertEqual(v1, BlockVersion.loads('user/math : 3'))
        self.assertEqual(v1, BlockVersion.loads(' user/math(master): 3 '))
        self.assertEqual(v1, BlockVersion.loads('user/math (master) : 3 '))
        self.assertEqual(v1, BlockVersion.loads('user/math (user/master) : 3 '))
        self.assertEqual('user/math: 3', str(v1))

        v1 = BlockVersion("user/user/math/branch", 3)
        self.assertEqual(v1, BlockVersion.loads('user/math(branch): 3'))
        self.assertEqual(v1, BlockVersion.loads('user/math (user/branch) : 3'))
        self.assertEqual('user/math(branch): 3', str(v1))

        v1 = BlockVersion("user2/user/math/branch", 3)
        self.assertEqual(v1, BlockVersion.loads('user/math (user2/branch) : 3'))
        self.assertEqual('user/math(user2/branch): 3', str(v1))

        v1 = BlockVersion("user/user/math/master", None)
        self.assertEqual(v1, BlockVersion.loads(' user/math '))
        self.assertEqual(v1, BlockVersion.loads(' user/math(master) '))
        self.assertEqual(v1, BlockVersion.loads('user/math (user/master) '))
        self.assertEqual('user/math', str(v1))

        v1 = BlockVersion("user/user/math/branch", None)
        self.assertEqual(v1, BlockVersion.loads('user/math(branch) '))
        self.assertEqual(v1, BlockVersion.loads('user/math (user/branch)'))
        self.assertEqual('user/math(branch)', str(v1))

        v1 = BlockVersion("user2/user/math/branch", None)
        self.assertEqual(v1, BlockVersion.loads('user/math (user2/branch) '))
        self.assertEqual('user/math(user2/branch)', str(v1))

        v1 = BlockVersion("user/user/math/master", 30, '2.7.1')
        self.assertEqual(v1, BlockVersion.loads('user/math : 30 @2.7.1'))
        self.assertEqual(v1, BlockVersion.loads('user/math : 30 @2.7.1# This is a comment'))
        self.assertEqual(v1, BlockVersion.loads('user/math : 30 @2.7.1  # This is a comment'))
        self.assertEqual('user/math: 30 @2.7.1', str(v1))

        v1 = BlockVersion("dummy/dummy/myblock/master", -1)
        self.assertEquals(v1, BlockVersion.loads('dummy/myblock: -1'))

        v1 = BlockVersion("dummy/dummy/my-block/master", 2)
        self.assertEquals(v1, BlockVersion.loads('dummy/my-block: 2'))

        v1 = BlockVersion("user0/user0/hello-.__--1/master", 0)
        self.assertEquals(v1, BlockVersion.loads('user0/hello-.__--1: 0'))

        with self.assertRaisesRegexp(BiiException, "Bad block version format"):
            BlockVersion.loads('laso/block:invalidversion')

        v1 = BlockVersion("dummy/dummy/first/master", None, "1.12")
        self.assertEquals(v1, BlockVersion.loads('dummy/first @1.12'))

        v1 = BlockVersion.loads("user/math: @DEV ")
        self.assertEqual(v1.block, "user/user/math/master")
        self.assertEqual(v1.time, None)
        self.assertEqual(v1.tag, "DEV")

        v1 = BlockVersion.loads("user/math: 1 @1.2   # My comment")
        self.assertEqual(v1.block, "user/user/math/master")
        self.assertEqual(v1.time, 1)
        #FIXME: This will fail self.assertEqual(v1.tag, "DEV")

    def test_serialize(self):
        bv = BlockVersion("user/user/math/master", 3, '2.7.1')
        s = bv.serialize()
        d = BlockVersion.deserialize(s)
        self.assertEquals(bv, d)

        bv = BlockVersion("user/user/math/master", 3)
        s = bv.serialize()
        d = BlockVersion.deserialize(s)
        self.assertEquals(bv, d)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
