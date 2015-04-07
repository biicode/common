import unittest
from biicode.common.model.bii_type import BiiType, CPP, TEXT, XML, HTML, IMAGE, PYTHON, UNKNOWN, \
    SOUND


class BiiTypeTest(unittest.TestCase):

    def test_bii_types_from_name(self):
        self.assertEqual(CPP, BiiType.from_extension(".cpp"))
        self.assertEqual(CPP, BiiType.from_extension(".c"))
        self.assertEqual(CPP, BiiType.from_extension(".ino"))
        self.assertEqual(CPP, BiiType.from_extension(".h"))
        self.assertEqual(CPP, BiiType.from_extension(".hh"))
        self.assertEqual(CPP, BiiType.from_extension(".cc"))
        self.assertEqual(CPP, BiiType.from_extension(".inl"))
        self.assertEqual(CPP, BiiType.from_extension(".ipp"))
        self.assertEqual(TEXT, BiiType.from_extension(".txt"))
        self.assertEqual(XML, BiiType.from_extension(".xml"))
        self.assertEqual(HTML, BiiType.from_extension(".html"))
        self.assertEqual(HTML, BiiType.from_extension(".htm"))
        self.assertEqual(SOUND, BiiType.from_extension(".wav"))
        self.assertEqual(IMAGE, BiiType.from_extension(".jpg"))
        self.assertEqual(IMAGE, BiiType.from_extension(".gif"))
        self.assertEqual(IMAGE, BiiType.from_extension(".png"))
        self.assertEqual(IMAGE, BiiType.from_extension(".bmp"))
        self.assertEqual(PYTHON, BiiType.from_extension(".py"))
        self.assertEqual(TEXT, BiiType.from_extension(".bii"))
        self.assertEqual(UNKNOWN, BiiType.from_extension(".unknow"))

    def test_set_of_types(self):
        self.assertFalse(BiiType.from_extension(".cpp").is_binary())
        self.assertTrue(BiiType.from_extension(".wav").is_binary())
        self.assertTrue(BiiType.from_extension(".cpp") == CPP)

if __name__ == "__main__":
    unittest.main()
