import unittest

from biicode.common.dev.system_id import SystemID
from biicode.common.settings.version import Version


class SystemIDTest(unittest.TestCase):

    def setUp(self):
        self.sut = SystemID("open_gl", "CPP")

    def test_set_generic_system(self):
        self.sut.set_generic_system()
        self.assertEquals(self.sut.language_version, Version())

    def test_version_id_setter_exception(self):
        self.assertRaises(ValueError, self.sut.version_id, 1)

    def test_version_id_setter_with_version_instance(self):
        self.sut.version_id = Version()

    def test_version_id_setter_with_string(self):
        self.sut.version_id = "1"

    def test_language_version_id_setter_with_version_instance(self):
        self.sut.language_version = Version()
        self.assertEquals(self.sut.language_version, Version())

    def test_language_version_id_setter_with_string(self):
        self.sut.language_version = "1"
        self.assertEquals(self.sut.language_version, Version("1"))

    def test_equal(self):
        self.assertTrue(self.sut == self.sut)
        self.assertFalse(self.sut == 1)
