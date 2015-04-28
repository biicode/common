from biicode.common.exception import (PublishException, UpToDatePublishException,
                                      ForbiddenException, AuthenticationException)
from biicode.common.edition import changevalidator
from biicode.common.diffmerge.compare import compare
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.publish.publish_request import PublishRequest
from biicode.common.edition.block_holder import BIICODE_FILE


def update_config(new_parent_version, hive_holder):
    """ after a publication, the parent version has to be updated
    """
    assert isinstance(new_parent_version, BlockVersion)
    assert new_parent_version.time is not None
    assert new_parent_version.time != -1

    block_name = new_parent_version.block_name
    block_holder = hive_holder[block_name]
    block_holder.parent = new_parent_version

    block_holder.commit_config()

    for block_holder in hive_holder.block_holders:
        requirements = block_holder.requirements
        if block_name in requirements:
            requirements.add_version(new_parent_version)
        block_holder.commit_config()


def block_changed(changes, block_holder, other_holder):
    if other_holder is None:
        return True
    if len(changes) == 1 and len(changes.modified) == 1 and BIICODE_FILE in changes.modified:
        return block_holder.config.changed(other_holder.config)
    return len(changes) > 0


def build_publish_request(biiapi, hive_holder, block_name, tag, msg,
                          versiontag, origin, biiout):
    block_name, dep_block_names = _check_input(hive_holder, block_name)
    _check_dep_blocks(biiapi, hive_holder, dep_block_names, biiout)
    block_holder = hive_holder[block_name]
    if not changevalidator.check_block_size(block_holder, biiout):
        raise PublishException("Block is too large to be published")

    parent = block_holder.parent
    _check_possible(parent, biiapi, biiout)

    if parent.time != -1:  # Update
        remote_block_holder = biiapi.get_block_holder(parent)
        base_resources = remote_block_holder.resources
        parent_delta_info = biiapi.get_version_delta_info(parent)
    else:  # New block
        base_resources = None
        parent_delta_info = None
        remote_block_holder = None

    changes = compare(base_resources, block_holder.resources)
    if not block_changed(changes, block_holder, remote_block_holder):
        if parent_delta_info and tag > parent_delta_info.tag:
            biiout.info('No changes, promoting tag %s -> %s' % (parent_delta_info.tag, tag))
            changes.modified.pop(BIICODE_FILE, None)
        else:
            raise UpToDatePublishException("Up to date, nothing to publish")
    changes.deduce_renames()

    request = PublishRequest()
    request.parent = parent
    request.changes = changes
    if parent_delta_info:
        request.parent_time = parent_delta_info.date
    assert all(bv.time is not None for bv in block_holder.requirements.itervalues())
    request.deptable = block_holder.requirements
    request.tag = tag
    request.msg = msg
    request.versiontag = versiontag
    request.origin = origin
    return request


def _check_input(hive_holder, block_name):
    '''basics checks: block_name in hive and in block_graph, and the graph
    (just the SRC graph) has no cycles
    param block_name: Can be None
    return: (block_name, set(BlockName)) of dependents blocks in blocks folder'''

    assert(block_name is not None)
    if block_name not in hive_holder.blocks:
        raise PublishException('Block "%s" does not exist in your project' % block_name)

    hive_dependencies = hive_holder.hive_dependencies
    gr = hive_dependencies.version_graph
    cycles = gr.get_cycles()
    if cycles:
        raise PublishException('There is a cycle between your blocks: %s\n'
                               'Please fix it. Aborting publication' % cycles)

    if block_name not in gr.versions:
        raise PublishException('Block %s not in current graph. Aborting publication.\n'
                               'This seems a biicode internal error, please contact us'
                               % block_name)

    versions = gr.versions[block_name]
    assert len(versions) == 1
    version = iter(versions).next()
    dependent_versions = gr.compute_closure(version)
    dep_blocks = {v.block_name for v in dependent_versions if v.block_name in hive_holder.blocks}
    return block_name, dep_blocks


def _check_dep_blocks(biiapi, hive_holder, dep_blocks, biiout):
    '''check that the dependent blocks have no modifications'''
    modified = False

    parents = {b.parent.block_name: b.parent for b in hive_holder.block_holders}
    for block_name in dep_blocks:
        edition_block_holder = hive_holder[block_name]
        # Modify requirements (only in memory) for comparison _block_changed below
        requirements = edition_block_holder.requirements
        for parent_name, parent in parents.iteritems():
            if parent_name in requirements:
                requirements.add_version(parent)
        # Now check parents
        parent = edition_block_holder.parent
        if parent.time == -1:
            modified = True
            biiout.error('Block %s has never been published. Publish it first' % (block_name))
        else:
            remote_block_holder = biiapi.get_block_holder(parent)
            changes = compare(remote_block_holder.resources, edition_block_holder.resources)
            if block_changed(changes, edition_block_holder, remote_block_holder):
                modified = True
                biiout.error('Block %s is modified. Publish it first' % (block_name))
    if modified:
        raise PublishException('There are modified blocks that must be published first')


def _check_possible(parent, biiapi, biiout):
    no_permissions_message = 'Unauthorized publication to "%s"' % str(parent)

    try:
        # If no logged username, can't publish, so force signin
        biiapi.require_auth()
    except (ForbiddenException, AuthenticationException):
        raise PublishException(no_permissions_message)

    try:
        block_info = biiapi.get_block_info(parent.block)
        private_str = "private" if block_info.private else "public "
        biiout.info("*****************************")
        biiout.info("***** Publishing %s****" % private_str)
        biiout.info("*****************************")
    except ForbiddenException:
        raise PublishException(no_permissions_message)

    if not block_info.can_write:
        raise PublishException("You don't have permission to publish in %s" % str(parent))

    if block_info.last_version.time != parent.time:
        if block_info.last_version.time == -1:
            raise PublishException("You are outdated, you are modifying %s\n"
                                   "    but the block is empty or has been deleted\n"
                                   "    Delete your [parent] to be able to publish again\n"
                                   % (str(parent)))
        else:
            raise PublishException("You are outdated, you are modifying %s\n"
                                   "    but last version is %s\n"
                                   "    You can:\n"
                                   "        - 'bii update' to integrate changes\n"
                                   "        -  modify your [parent] to discard last version\n"
                                   "        -  close and open your block to discard your changes\n"
                                   % (str(parent), str(block_info.last_version)))
