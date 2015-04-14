import unittest
from biicode.common.model.renames import Renames
from biicode.common.model.brl.cell_name import CellName
from biicode.common.utils.serializer import serialize


class RenamesTest(unittest.TestCase):
    '''Renames class tests'''

    def test_basic(self):
        r = Renames()
        r[CellName('a.h')] = CellName('a.h')
        self.assertEqual(0, len(r))

    def test_double_rename(self):
        r = Renames()
        r[CellName('a.h')] = CellName('b.h')
        r[CellName('b.h')] = CellName('c.h')
        self.assertEqual(r[CellName('a.h')], CellName('b.h'))
        self.assertEqual(r[CellName('b.h')], CellName('c.h'))

    def test_get_old_name(self):
        r = Renames()
        r[CellName('a.h')] = CellName('b.h')
        r[CellName('b.h')] = CellName('c.h')
        self.assertEqual('a.h', r.get_old_name('b.h'))

    def test_cat(self):
        r = Renames()
        r[CellName('a.h')] = CellName('b.h')

        r2 = Renames()
        r2[CellName('b.h')] = CellName('c.h')
        r2[CellName('d.h')] = CellName('e.h')
        r.cat(r2)
        self.assertEqual(r[CellName('a.h')], CellName('c.h'))
        self.assertEqual(r[CellName('d.h')], CellName('e.h'))
        self.assertEqual(2, len(r))

    def test_serialize(self):
        r = Renames()
        r[CellName('a.h')] = CellName('b.h')
        r[CellName('b.h')] = CellName('c.h')
        s = serialize(r)
        d = Renames.deserialize(s)
        self.assertIsInstance(d, Renames)
        self.assertEqual(r, d)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
