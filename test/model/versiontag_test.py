import unittest
from biicode.common.model.version_tag import VersionTag, ALPHA, BETA, STABLE, DEV


class VersionTagTest(unittest.TestCase):

    def test_basic(self):
        tag = ALPHA
        self.assertEqual(ALPHA, tag)
        self.assertNotEqual(BETA, tag)
        self.assertTrue(ALPHA == tag)
        self.assertFalse(BETA == tag)
        self.assertGreater(STABLE, BETA)
        self.assertGreater(tag, DEV)

        tag2 = BETA
        self.assertLess(tag, tag2)

    def test_value_error(self):
        self.assertRaises(ValueError, VersionTag, 5)
        self.assertRaises(ValueError, VersionTag, -1)
        self.assertRaises(ValueError, VersionTag, 'hi')
