from biicode.common.edition.hive import Hive
from biicode.common.exception import BiiSerializationException
from biicode.common.test.bii_test_case import BiiTestCase


class HiveTest(BiiTestCase):
    def setUp(self):
        self.hive = Hive()

    def test_serialize(self):
        serial = self.hive.serialize()
        deserial = Hive.deserialize(serial)
        self.assert_bii_equal(Hive(), deserial)

    def test_deserialization(self):
        self.assertRaises(BiiSerializationException, Hive.deserialize, None)
