import unittest
import math

from biicode.common.diffmerge.compare import compare
from biicode.common.model.brl.cell_name import CellName


class Int(int):
    def similarity(self, other):
        return math.exp(-abs(self - other) / 5.0)


class CompareTest(unittest.TestCase):

    def test_deduce_renames(self):
        ''' 2 is modified from 2 to 22
            3 is deleted
            5 is renamed to 6 (5 deleted, 6 created)
            10 is created'''
        base_resources = {CellName('1'): Int(1), CellName('2'): Int(2),
                          CellName('3'): Int(3), CellName('4'): Int(4),
                          CellName('5'): Int(5)}
        other_resources = {CellName('1'): Int(1), CellName('2'): Int(22),
                           CellName('4'): Int(4), CellName('6'): Int(6),
                           CellName('10'): Int(10)}

        #compute changes without renames
        changes = compare(base_resources, other_resources)
        self.assertEqual({CellName('3'): 3, CellName('5'): 5}, changes.deleted)
        self.assertEqual({CellName('6'): Int(6), CellName('10'): 10}, changes.created)
        self.assertEqual({CellName('2'): (2, 22)}, changes.modified)
        self.assertEqual({}, changes.renames)

        #deduce renames
        changes.deduce_renames()
        #nothing changes
        self.assertEqual({CellName('3'): 3, CellName('5'): 5}, changes.deleted)
        self.assertEqual({CellName('6'): Int(6), CellName('10'): 10}, changes.created)
        self.assertEqual({CellName('2'): (2, 22)}, changes.modified)
        #but the renames field
        self.assertEqual({CellName('5'): CellName('6')}, changes.renames)

    def test_deduce_renames_multi_all_equal(self):
        '''2 is deleted
           3 is created with 2's contents
           4 is created with 2's contents
           2 is considered to be renamed to 4
        '''
        #FIXME: Conclusion is arbitrary. Last one to be processed with equal similarty degreee
        # is the one choosen. We might have to inform the user about this
        base_resources =  {CellName('1'): Int(1), CellName('2'): Int(2)}
        other_resources = {CellName('1'): Int(1),
                           CellName('3'): Int(2), CellName('4'): Int(2)}

        #compute changes without renames
        changes = compare(base_resources, other_resources)
        changes.deduce_renames()
        #nothing changes
        self.assertEqual({CellName('2'): 2}, changes.deleted)
        self.assertEqual({CellName('3'): Int(2), CellName('4'): 2}, changes.created)
        self.assertEqual({}, changes.modified)
        self.assertEqual({CellName('2'): CellName('4')}, changes.renames)

    def test_deduce_renames_multi_different_values(self):
        '''2 is deleted
           3 is created with 3
           4 is created with 4
           2 is considered to be renamed to 3
        '''
        base_resources =  {CellName('1'): Int(1), CellName('2'): Int(2)}
        other_resources = {CellName('1'): Int(1),
                           CellName('3'): Int(3), CellName('4'): Int(4)}

        #compute changes without renames
        changes = compare(base_resources, other_resources)
        changes.deduce_renames()
        #nothing changes
        self.assertEqual({CellName('2'): 2}, changes.deleted)
        self.assertEqual({CellName('3'): Int(3), CellName('4'): 4}, changes.created)
        self.assertEqual({}, changes.modified)
        self.assertEqual({CellName('2'): CellName('3')}, changes.renames)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
