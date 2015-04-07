import unittest

from biicode.common.model.id import ID, UserID


class IDTest(unittest.TestCase):

    def test_build_str(self):
        user = UserID(1)
        mod = user + 2
        res = mod + 3
        con = mod + 4

        self.assertEquals('1:2:3', str(res))
        self.assertEquals('1:2:4', str(con))

    def test_hasheable(self):
        user = UserID(1)
        mod = user + 2
        r1 = mod + 3
        r2 = mod + 4
        r3 = mod + 5
        s = set()
        s.add(r1)
        s.add(r2)
        s.add(r3)
        s.add(r1)
        s.add(r2)
        self.assertEquals(3, len(s))

    def test_byte_order(self):
        i1 = ID((1, 2, 3))
        bin_id = i1.serialize()
        for i in [0, 1, 2, 4, 5, 6, 8, 9, 10]:
            self.assertEqual('\x00', bin_id[i])
        self.assertEqual('\x01', bin_id[3])
        self.assertEqual('\x02', bin_id[7])
        self.assertEqual('\x03', bin_id[11])
