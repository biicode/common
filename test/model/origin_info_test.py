import unittest
from biicode.common.model.origin_info import OriginInfo


class OriginInfoTest(unittest.TestCase):

    def test_serialization(self):
        origin = OriginInfo("https://github.com/lasote/openssl",
                            "OpenSSL_1_0_2_biicode",
                            "biicode_1_0_1l",
                            "9012312387162361287361923")

        self._assert_serialization(origin)

        origin = OriginInfo("https://github.com/lasote/openssl",
                            None,
                            "biicode_1_0_1l",
                            None)

        self._assert_serialization(origin)

    def _assert_serialization(self, ob1):
        serial = ob1.serialize()
        ob2 = OriginInfo.deserialize(serial)

        self._assert_equal(ob1, ob2)

    def _assert_equal(self, ob1, ob2):
        self.assertEqual(ob1.url, ob2.url)
        self.assertEqual(ob1.branch, ob2.branch)
        self.assertEqual(ob1.tag, ob2.tag)
        self.assertEqual(ob1.commit, ob2.commit)
