import unittest

from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.brl.cell_name import CellName
from biicode.common.exception import InvalidNameException


class BlockCellNameTest(unittest.TestCase):

    def test_basic(self):
        m = BlockCellName("User\Module/Path/to/file.h")
        self.assertEqual('User/Module/Path/to/file.h', m)
        self.assertEqual('User/Module', m.block_name)
        self.assertEqual('Path/to/file.h', m.cell_name)

        m = BlockCellName("user/Module/Path/to/CamelCase.java")
        self.assertEqual('user/Module/Path/to/CamelCase.java', m)
        self.assertEqual('user/Module', m.block_name)
        self.assertEqual('Path/to/CamelCase.java', m.cell_name)

        m = BlockCellName("User_1/Block_1/Path/to/under_score.py")
        self.assertEqual('User_1/Block_1/Path/to/under_score.py', m)
        self.assertEqual('User_1/Block_1', m.block_name)
        self.assertEqual('Path/to/under_score.py', m.cell_name)

        # Valid patterns
        BlockCellName("User/Modu/Path$/to/CamelCase.h")
        BlockCellName("User/Modu/Path/to$/CamelCase.cpp")

    def test_non_valid(self):
        self.assertRaises(InvalidNameException, BlockCellName, "user/-.-.-./*****/m#")
        self.assertRaises(InvalidNameException, BlockCellName, "User/Module/Path/to/ file.h")
        self.assertRaises(InvalidNameException, BlockCellName, "User/Module\/Path/to/ file.h")
        self.assertRaises(InvalidNameException, BlockCellName, "User/Modu$/Path/to/CamelCase.h")

    def test_add(self):
        mName = BlockName("user2/module2")
        m = mName + "path/to/file2.h"
        self.assertEqual('user2/module2/path/to/file2.h', m)
        self.assertEqual('user2/module2', m.block_name)
        self.assertEqual('user2', m.block_name.user)
        self.assertEqual('path/to/file2.h', m.cell_name)
        self.assertEqual('.h', m.extension)

        m = mName + CellName("path/to/file2.h")
        self.assertEqual('user2/module2/path/to/file2.h', m)
        self.assertEqual('user2/module2', m.block_name)
        self.assertEqual('user2', m.block_name.user)
        self.assertEqual('path/to/file2.h', m.cell_name)
        self.assertEqual('.h', m.extension)

    def test_username(self):
        m = BlockCellName("User/Module/Path/to/file.h")
        self.assertEqual('User', m.user_name)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
