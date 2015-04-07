from biicode.common.model.brl.block_name import BlockName
from biicode.common.edition.hiveprocessor import (blocks_process, deps_process,
                                                  compute_src_graph, compute_common_table)
from biicode.common.edition.processors.processor_changes import ProcessorChanges
from biicode.common.edition.checkin import checkin_files, checkin_block_files
from biicode.common.exception import BiiException, UpToDatePublishException,\
    PublishException
from biicode.common.publish.publish_manager import block_changed
from biicode.common.migrations.biiconfig_migration import migrate_bii_config
from biicode.common.edition.open_close import select_version


class HiveManager(object):
    '''This class is the main entry point for operations over bii-model hives,
    i.e. hives on the biicode model and db, NOT in disk. Check the client
    HiveDiskImage for operations over the disk image of a hive'''

    def __init__(self, edition_api, biiapi, biiout):
        ''' Params:
        * edition_api: is compulsory
        * biiapi: some edition operation probably do not require
        '''
        self._edition = edition_api
        self._biiapi = biiapi
        self._biiout = biiout
        # transient, cached values
        self._hive = None
        self._hive_holder = None

    def publish(self, block_name, tag, msg, versiontag, publish_all, origin):
        """
        param block_name: can be None, if just one block exist
        """
        from biicode.common.model.version_tag import DEV
        if publish_all and block_name:
            raise BiiException('Do not specify "block name" and "all" option')
        if (tag is None or tag is DEV) and versiontag is not None:
            raise BiiException('DEV versions cannot have a version tag')
        if tag is None:
            tag = DEV
            self._biiout.info('Publishing using DEV tag. '
                              'Previous DEV publication (if any) will be overwritten')

        if not publish_all:
            return self._publish_one(block_name, tag, msg, versiontag, origin)
        else:
            # Be careful, return array of versions
            return self._publish_all(tag, msg, versiontag)

    def _get_target_block_name(self, block_name):
        """Check if block_name is a valid block or if block_name is none check
        if there is only one block in the hive. Otherwise it raises an exception"""

        blocks = self.hive_holder.blocks
        current_blocks = '\nCurrent project blocks:\n\t' + '\n\t'.join(blocks)
        if block_name is None:
            if len(blocks) == 1:
                return iter(blocks).next()
            else:
                raise BiiException('%s\nMore than one block in this project!' % current_blocks)
        if block_name not in self.hive_holder.blocks:
            raise BiiException('%s\nBlock "%s" does not exist in your project'
                               % (current_blocks, block_name))
        return block_name

    def _publish_one(self, block_name, tag, msg, versiontag, origin):
        from biicode.common.publish.publish_manager import build_publish_request
        from biicode.common.publish.publish_manager import update_config

        # Check block_name or get the only one if block_name is None
        try:
            block_name = self._get_target_block_name(block_name)
        except BiiException as exc:
            raise BiiException(str(exc) + '\nPlease specify block to publish\n'
                               'with "$ bii publish my_user/my_block"')

        hive_holder = self.hive_holder
        request = build_publish_request(self._biiapi, hive_holder, block_name,
                                        tag, msg, versiontag, origin, self._biiout)

        try:
            self._biiout.debug("Sending publish request to server")
            version = self._biiapi.publish(request)
        except BiiException as e:
            raise PublishException('Publication failed in server!\n%s' % e.message)

        update_config(version, self._edition, hive_holder)
        self._biiout.info('Successfully published %s\n' % str(version))
        return version

    def _publish_all(self, tag, msg, versiontag):
        src_graph = self.hive_holder.hive.hive_dependencies.src_graph
        levels = src_graph.get_levels()
        versions = []
        for level in levels:
            for block_version in level:
                try:
                    v = self._publish_one(block_version.block_name, tag, msg, versiontag, None)
                    versions.append(v)
                except UpToDatePublishException:
                    pass
        return versions

    @property
    def hive_holder(self):
        if self._hive_holder is None:
            self._hive_holder = self._edition.get_holder(self.hive)
        return self._hive_holder

    @property
    def hive(self):
        if self._hive is None:
            self._hive = self._edition.read_hive()
        return self._hive

    @property
    def closure(self):
        hive = self.hive
        return hive.hive_dependencies.closure

    def update(self, block_name=None, time=None):
        """ a block is outdated, because someone has published from another location,
        and parent is not the last one in the block anymore.
        update is able to merge with the given time
        param time: Can be None=> means the last one
        param block_name: The block to be updated
        """
        from biicode.common.diffmerge.update import update

        hive_holder = self.hive_holder
        # TODO: Copied from publish: refactor
        if block_name is None:
            blocks = hive_holder.blocks
            if len(blocks) == 1:
                block_name = iter(blocks).next()
            else:
                raise BiiException('More than one block in this project %s\n'
                                   'Please specify block to update\n'
                                   'with "$ bii update my_user/my_block"')
        try:
            block_holder = hive_holder[block_name]
        except KeyError:
            raise BiiException("Block %s is not open" % block_name)

        files, other_version = update(block_holder, time, self._biiapi, self._biiout)

        # Extra "process" after the update
        proc_changes = ProcessorChanges()
        checkin_block_files(hive_holder, block_name, files, proc_changes, self._biiout)
        blocks_process(hive_holder, proc_changes, self._biiout)
        deps_process(self._biiapi, hive_holder, proc_changes, self._biiout)
        block_holder = hive_holder[block_name]
        block_holder.parent = other_version
        new_config = block_holder.commit_config()
        if new_config:
            proc_changes.upsert(new_config.name, new_config.content, True)
        self._edition.save_hive_changes(hive_holder.hive, proc_changes)
        return block_name

    def process(self, settings, files):
        hive_holder = self.hive_holder
        delete_migration = migrate_bii_config(files, self._biiout)
        processor_changes = checkin_files(hive_holder, settings, files, self._biiout)
        blocks_process(hive_holder, processor_changes, self._biiout)
        deps_process(self._biiapi, hive_holder, processor_changes, self._biiout, settings)
        self._edition.save_hive_changes(hive_holder.hive, processor_changes)
        return delete_migration

    def find(self, policy=None, **find_args):
        # Imports are local, cause only used in this function, avoid loading modules for
        # every execution
        from biicode.common.find import find_manager
        from biicode.common.find.policy import Policy

        policy = policy or Policy.default()

        hive_holder = self.hive_holder
        return find_manager.find(self._biiapi, hive_holder, self._biiout, policy, **find_args)

    def apply_find_result(self, find_result):
        from biicode.common.find import find_manager

        if find_result:
            hive_holder = self.hive_holder
            processor_changes = ProcessorChanges()
            find_manager.update_hive_with_find_result(hive_holder, find_result, processor_changes)
            blocks_process(hive_holder, processor_changes, self._biiout)
            deps_process(self._biiapi, hive_holder, processor_changes, self._biiout)
            self._edition.save_hive_changes(hive_holder.hive, processor_changes)

    def open(self, block_name, track, time, version_tag):
        '''
        Opens a block
        Params:
            block_version: If time is None last version is retrieved
        Returns:
            block_version actually opened
        '''
        from biicode.common.edition.open_close import open_block

        hive_holder = self.hive_holder
        block_version = select_version(hive_holder, self._biiapi, self._biiout, block_name,
                                       track, time, version_tag)
        processor_changes = open_block(hive_holder, block_version, self._biiapi, self._biiout)
        try:
            blocks_process(hive_holder, processor_changes, self._biiout)
            deps_process(self._biiapi, hive_holder, processor_changes, self._biiout)
        finally:
            self._edition.save_hive_changes(hive_holder.hive, processor_changes)
        return block_version

    def close(self, block_name, settings=None, force=False):
        from biicode.common.edition.open_close import close_block
        assert isinstance(block_name, BlockName)

        if block_name not in self.hive_holder.blocks:
            raise BiiException("Block %s is not in your project, you cannot close it"
                               % str(block_name))

        parent = self.hive_holder[block_name].parent
        if parent.time == -1:
            raise BiiException("Block %s is not published, you cannot close it."
                               "\nIf you want to delete it, delete the folder in the filesystem."
                               % str(block_name))

        remote_block_holder = self._biiapi.get_block_holder(parent)
        from biicode.common.diffmerge.compare import compare
        changes = compare(remote_block_holder.resources, self.hive_holder[block_name].resources)
        if block_changed(changes, self.hive_holder[block_name], remote_block_holder) and not force:
            raise BiiException("Block %s has unpublished changes.\n%s\n"
                               "Execute with --force to ignore them or publish it first."
                               % (str(block_name), str(changes)))

        processor_changes = close_block(self.hive_holder, block_name)
        blocks_process(self.hive_holder, processor_changes, self._biiout)
        deps_process(self._biiapi, self.hive_holder, processor_changes, self._biiout, settings)
        self._edition.save_hive_changes(self.hive_holder.hive, processor_changes)
