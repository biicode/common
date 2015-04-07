import unittest
from biicode.common.model.brl.brl_user import BRLUser
from biicode.common.model.brl.block_name import BlockName
from biicode.common.exception import InvalidNameException


class TestBRLUser(unittest.TestCase):
    def testName(self):
        user = BRLUser('username')
        self.assertEqual('username', user)
        user2 = BRLUser('Username   ')
        self.assertEqual('Username', user2)
        self.assertNotEqual(user, user2)

    def test_brluser_underscore(self):
        user = BRLUser('username_1')
        self.assertEqual('username_1', user)

    def testName2(self):
        with self.assertRaises(InvalidNameException):
            BRLUser('us&%')
        with self.assertRaises(InvalidNameException):
            BRLUser('us.')

    def test_create_blockname(self):
        user = BRLUser("user2")
        bn = user.create_block_name("block2")
        self.assertIsInstance(bn, BlockName)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
