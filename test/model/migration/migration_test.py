import unittest
from biicode.common.migrations.migration import Migration
import time


class MigrationTest(unittest.TestCase):

    def test_compare(self):
        mig1 = Migration()
        self.assertEqual(mig1.ID, "Migration")
        mig1.ID = "0_new_migration"
        mig1.applied_timestamp = time.time()
        mig2 = Migration()
        mig2.ID = "1_new_migration"
        mig2.applied_timestamp = mig1.applied_timestamp
        self.assertNotEqual(mig1, mig2)

        self.assertEquals(mig1, mig1)

        mig1_copy = Migration()
        mig1_copy.ID = "0_new_migration"
        mig1_copy.applied_timestamp = mig1.applied_timestamp

        self.assertEquals(mig1, mig1_copy)

    def test_serialize(self):

        mig1 = Migration()
        mig1.ID = "0_new_migration"
        mig1.applied_timestamp = time.time()
        ser = mig1.serialize()
        des = Migration.deserialize(ser)

        self.assertEqual(mig1, des)
        self.assertEqual(des.ID, "0_new_migration")
