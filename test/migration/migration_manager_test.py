import unittest
from mock import Mock
from biicode.common.migrations.migration_manager import MigrationManager
from biicode.common.test.migration.migration_utils import TMigration1,\
    TMigration2, TMigration3
from biicode.common.exception import BiiException


class MigrationManagerTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.mig1 = TMigration1()
        self.mig2 = TMigration2()
        self.mig3 = TMigration3()

        self.store = Mock()
        self.store.store_executed_migration = Mock()
        self.migration_manager = MigrationManager(self.store,
                                                  [self.mig1, self.mig2, self.mig3],
                                                  Mock())

    def test_migrate_nothing(self):
        # Last is last migrated, nothing to do
        self.store.read_last_migrated.return_value = self.mig3
        self.migration_manager.migrate()
        self.assertFalse(self.mig1.migrate.called)
        self.assertFalse(self.mig2.migrate.called)
        self.assertFalse(self.mig3.migrate.called)

        self.assertEqual(self.mig1.applied_timestamp, None)
        self.assertEqual(self.mig2.applied_timestamp, None)
        self.assertEqual(self.mig3.applied_timestamp, None)

        self.assertEquals(self.store.store_executed_migration.call_count, 0)

    def test_migrate_all(self):
        # Nothing is migrate, migrate all
        self.store.read_last_migrated.return_value = None
        self.migration_manager.migrate()
        self.assertTrue(self.mig1.migrate.called)
        self.assertTrue(self.mig2.migrate.called)
        self.assertTrue(self.mig3.migrate.called)

        self.assertNotEqual(self.mig1.applied_timestamp, None)
        self.assertNotEqual(self.mig2.applied_timestamp, None)
        self.assertNotEqual(self.mig3.applied_timestamp, None)

        self.assertEquals(self.store.store_executed_migration.call_count, 3)
        self.store.store_executed_migration.assert_called_with(self.mig3)

    def test_migrate_some(self):
        # 1 and 2 is migrated, lets migrate 3!
        self.store.read_last_migrated.return_value = self.mig2
        self.migration_manager.migrate()
        self.assertFalse(self.mig1.migrate.called)
        self.assertFalse(self.mig2.migrate.called)
        self.assertTrue(self.mig3.migrate.called)

        self.assertEqual(self.mig1.applied_timestamp, None)
        self.assertEqual(self.mig2.applied_timestamp, None)
        self.assertNotEqual(self.mig3.applied_timestamp, None)

        self.assertEquals(self.store.store_executed_migration.call_count, 1)
        self.store.store_executed_migration.assert_called_with(self.mig3)

    def test_migration_not_found(self):
        """Last Migration not found in local migrations,
        incompatible hive<=>biicode version """
        self.store.read_last_migrated.return_value = self.mig3
        # Now mig3 does not exist!
        self.migration_manager = MigrationManager(self.store,
                                                  [self.mig1, self.mig2],
                                                  Mock())

        self.assertRaises(BiiException, self.migration_manager.migrate)
