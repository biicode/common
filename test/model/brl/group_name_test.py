import unittest
from biicode.common.model.brl.group_name import BranchName

class BranchNameTest(unittest.TestCase):

    def test_basic(self):
        BranchName('user1/master')

    def test_underscore(self):
        BranchName('user_1/feature_7')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
