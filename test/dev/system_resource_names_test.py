import unittest
from biicode.common.dev.system_resource_names import SystemResourceNames
from biicode.common.dev.system_id import SystemID


class SystemResourceNamesTest(unittest.TestCase):

    def setUp(self):
        self.sut = SystemResourceNames(SystemID("open_gl", "CPP"))

    def test_add_names(self):
        self.sut.add_names(["stdio"])
        self.assertListEqual(self.sut.names, ["stdio"])

    def test_serialize(self):
        self.assertIsInstance(self.sut.serialize(), dict)

    def test_eq_true(self):
        self.assertTrue(self.sut.__eq__(self.sut))
        self.assertTrue(self.sut.__eq__(SystemResourceNames(SystemID("open_gl", "CPP"))))

    def test_eq_false(self):
        system_resource_names = SystemResourceNames(SystemID("open_gl", "CPP"))
        system_resource_names.add_names(["stdio"])
        self.assertFalse(self.sut.__eq__(system_resource_names))
        self.assertFalse(self.sut.__eq__(""))
