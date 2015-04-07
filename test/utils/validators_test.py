from biicode.common.utils.validators import valid_ip
import unittest


class ValidatorsTest(unittest.TestCase):

    def validate_ip_raises_test(self):
        self.assertRaises(ValueError, valid_ip, "e")

    def validate_ip_test(self):
        self.assertEquals(valid_ip("192.168.1.1"), "192.168.1.1")
