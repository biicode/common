import unittest
from biicode.common.model.brl.block_name import BlockName
from biicode.common.exception import InvalidNameException


class BlockNameTest(unittest.TestCase):

    def blockname_test(self):
        m = BlockName("user/block")
        self.assertEquals("user/block", str(m))
        m = BlockName("user/bLOck")
        self.assertEquals("user/bLOck", str(m))
        self.assertEquals('bLOck', str(m.name))
        m = BlockName("uSer/bLOck")
        self.assertEquals("uSer/bLOck", str(m))

    def blockname_underscore_test(self):
        bn = BlockName("user_1/block_1")

    def long_blockname_test(self):
        wrong_bn = "dummy/dummy/block/master"
        with self.assertRaisesRegexp(InvalidNameException,
                                     '%s is not a valid BlockName.' % wrong_bn):
            BlockName(wrong_bn)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
