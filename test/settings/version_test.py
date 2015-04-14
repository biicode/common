import unittest
from biicode.common.settings.version import Version


class VersionTest(unittest.TestCase):

    def test_major_minor_fix(self):
        v1 = Version("3.4.1")
        self.assertEquals("3.4.1", str(v1))
        self.assertEquals(3, v1.list[0])
        self.assertEquals(4, v1.list[1])
        self.assertEquals(1, v1.list[2])

    def test_cmake_version(self):
        v1 = Version("2.8.12.2")
        v2 = Version('2.8.9')
        self.assertGreater(v1, v2)
        self.assertLess(v2, v1)
        self.assertEquals(1, cmp(v1, v2))
        self.assertEquals(-1, cmp(v2, v1))

    def test_major(self):
        v1 = Version("3")
        self.assertEquals('3', str(v1))
        self.assertEquals(3, v1.list[0])

    def test_compare(self):
        v1 = Version("3.4.1")
        v2 = Version("3.4.2")
        v3 = Version("3.4.0")
        v4 = Version("3.4")

        self.assertEquals(0, cmp(v1, v1))
        self.assertEquals(-1, cmp(v1, v2))
        self.assertEquals(1, cmp(v1, v3))
        self.assertEquals(1, cmp(v1, v4))

        self.assertTrue(v1 == v1)
        self.assertTrue(v1 < v2)
        self.assertTrue(v2 > v1)
        self.assertTrue(v3 > v4)

        self.assertTrue(v1 == "3.4.1")

    def test_major_minor_fix_str(self):
        v1 = Version("3.4.1a")
        self.assertEquals("3.4.1a", str(v1))
        self.assertEquals(3, v1.list[0])
        self.assertEquals(4, v1.list[1])
        self.assertEquals('1a', v1.list[2])

    def test_major_str(self):
        v1 = Version("3a")
        self.assertEquals("3a", str(v1))
        self.assertEquals("3a", v1.list[0])

    def test_compare_str(self):
        v1 = Version("3.4.1a")
        v2 = Version("3.4.1b")
        v3 = Version("3.4.0")
        v4 = Version("3.4")

        self.assertEquals(0, cmp(v1, v1))
        self.assertEquals(-1, cmp(v1, v2))
        self.assertEquals(1, cmp(v1, v3))
        self.assertEquals(1, cmp(v1, v4))
