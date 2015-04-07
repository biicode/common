import time
import itertools
from biicode.common.exception import BiiException


class MigrationManager(object):
    """Runs the pending migration"""

    def __init__(self, migration_store, local_migrations, biiout):
        self._migration_store = migration_store
        self._local_migrations = local_migrations
        self._biiout = biiout

    def migrate(self, *args, **kwargs):
        """Run pending migrations"""
        all_pending = self._pending_migrations()
        if not all_pending:
            self._biiout.debug("Everything up to date\n")
            return

        for pending in all_pending:
            self._biiout.info("Migrating %s..." % pending.ID)  # , is to avoid printing newline
            n1 = time.time()
            pending.migrate(*args, **kwargs)
            pending.applied_timestamp = time.time()
            # Store in database
            self._migration_store.store_executed_migration(pending)
            n2 = time.time()
            self._biiout.info("  OK (elapsed: %s seconds)" % str(n2 - n1))

    def _pending_migrations(self):
        """Local migrations not executed yet"""
        try:
            last_migrated = self._migration_store.read_last_migrated()
        except SyntaxError:
            last_migrated = None
        if last_migrated is None:  # No migrations executed yet, do all
            return self._local_migrations

        tmp = itertools.dropwhile(lambda mig: mig.ID != last_migrated.ID, self._local_migrations)
        migs = [el for el in tmp]
        if not migs:
            ''' Last migrated not found in local migrations, it means we are editing
                with a previous incompatible version (back to previous version before
                edit with an upgraded version)'''
            raise BiiException("Your current biicode version is not compatible with your project."
                               " Please upgrade biicode version and try again.")

        return migs[1:]  # Don't want to return iterator nor last_migrated either
