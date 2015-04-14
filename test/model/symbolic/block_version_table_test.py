import unittest

from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.exception import BiiException

# reusable in other tests
test_dep_table1 = """# My comment
User1\\geom: 3
user2/ge-om2 :  4

# My comment2
user3\\geom3 (user3\\master) :  5
user4\\geom4 (user5\\branch) :  6
"""

test_dep_table1_normalized = """# My comment
User1/geom: 3
user2/ge-om2: 4

# My comment2
user3/geom3: 5
user4/geom4(user5/branch): 6
"""
expected_dep_table1 = BlockVersionTable([BlockVersion('User1/User1/geom/master', 3),
                                         BlockVersion('user2/user2/ge-om2/master', 4),
                                         BlockVersion('user3/user3/geom3/master', 5),
                                         BlockVersion('user5/user4/geom4/branch', 6)])


class BlockVersionTableTest(unittest.TestCase):

    def test_basic(self):
        brl1 = BRLBlock("user/user2/block/branch")
        v1 = BlockVersion(brl1, 1)
        brl2 = BRLBlock("user2/user3/block2/branch3")
        v2 = BlockVersion(brl2, 2)

        table = BlockVersionTable()
        table.add_version(v1)
        table.add_version(v2)

        self.assertEqual(v1, table['user2/block'])
        self.assertEqual(v2, table['user3/block2'])
        self.assertEqual(2, len(table))

    def test_loads_dumps(self):
        #testing loads
        table = BlockVersionTable.loads(test_dep_table1)
        self.assertEqual(expected_dep_table1, table)

        #dumps without file reference
        dump = table.dumps()
        self.assertIn('User1/geom: 3', dump)
        self.assertIn('user2/ge-om2: 4', dump)
        self.assertIn('user3/geom3: 5', dump)
        self.assertIn('user4/geom4(user5/branch): 6', dump)

        #dump with file, without changes
        text = table.dumps(test_dep_table1)
        self.assertEqual(test_dep_table1_normalized, text)

        #dump with changes
        table['User1/geom'] = BlockVersion('user1/user1/geom/branch2', 13)

        #dump with file, without changes
        expected = '\n'.join(['# My comment',
                'user1/geom(branch2): 13',
                'user2/ge-om2: 4',
                '',
                '# My comment2',
                'user3/geom3: 5',
                'user4/geom4(user5/branch): 6',
                ''
                ])
        text = table.dumps(text)
        self.assertEqual(expected, text)

    def test_loads_error(self):
        self.assertRaisesRegexp(BiiException,
                                '1: Parse error: \n\tBad block version format "My comment"',
                                BlockVersionTable.loads, "My comment")
        self.assertRaisesRegexp(BiiException,
                                '2: merge conflict',
                                BlockVersionTable.loads, "#My comment\n<<<<<<<< asd sd")

        self.assertRaisesRegexp(BiiException,
                                '4: Parse error: \n\tDuplicate dependency "user1/geom\(tr2\): 4"',
                                BlockVersionTable.loads, ('# My comment\n'
                                                            'user1\\geom(user1\\tr2): 13\n'
                                                            '# My comment2\n'
                                                            'user1\\geom (user1\\tr2): 4\n'))
