from biicode.common.model.resource import Resource
from biicode.common.exception import BiiException
from biicode.common.edition.processors.processor_changes import ProcessorChanges
from biicode.common.migrations.biiconfig_migration import migrate_block_holder
from biicode.common.model.symbolic.block_version import BlockVersion


def select_version(hive_holder, biiapi, biiout, block_name, track, time, version_tag):
    dependencies = hive_holder.hive_dependencies.dep_graph.nodes
    dep_block_versions = {x.block_name: x for x in dependencies}
    existing_version = dep_block_versions.get(block_name)
    if existing_version:
        brl_block = block_name + track if track is not None else existing_version.block
        if time is None:
            if version_tag is not None:
                block_version = biiapi.get_version_by_tag(brl_block, version_tag)
            else:
                block_version = BlockVersion(brl_block, existing_version.time)
        else:
            block_version = BlockVersion(brl_block, time)
        if block_version != existing_version:
            biiout.warn("You had in your dependencies %s, but opening %s instead"
                              % (existing_version.to_pretty(), block_version.to_pretty()))
    else:  # Not in dependencies
        brl_block = block_name + track if track is not None else block_name.default_block()
        if time is None:
            if version_tag is not None:
                block_version = biiapi.get_version_by_tag(brl_block, version_tag)
            else:
                # If its an unrelated block we get last version
                block_info = biiapi.get_block_info(brl_block)
                block_version = block_info.last_version
        else:
            block_version = BlockVersion(brl_block, time)

    return block_version


def open_block(hive_holder, block_version, bii_api, biiout):
    '''Branches a block inside given hive'''
    block_name = block_version.block_name
    if block_name in hive_holder.blocks:
        parent_version = hive_holder[block_name].parent
        if parent_version.time == -1:
            parent_version = None
        raise BiiException('Block %s is already open with parent "%s"\n'
                           'You should close or delete it first, then try to open again'
                           % (block_name, parent_version))
    # Create the block holder
    block_holder = bii_api.get_block_holder(block_version)
    hive_holder.add_holder(block_holder)
    migrate_block_holder(block_holder, biiout)
    # Add resources from the block to the hive holder
    processor_changes = _process_resources(block_holder)
    # It is possible that is a published block without requirements
    if block_version.time > -1:
        open_dep_table = bii_api.get_dep_table(block_version)
        block_holder.requirements = open_dep_table
    # It is tracking the block_version
    block_holder.parent = block_version

    new_refs = block_holder.commit_config()
    if new_refs:
        processor_changes.upsert(new_refs.name, new_refs.content, blob_changed=True)

    hive_holder.hive.update(processor_changes)
    return processor_changes


def _process_resources(block_holder):
    processor_changes = ProcessorChanges()
    for (cell, content) in block_holder.simple_resources:
        # Cell from server has the CellID as ID, we need BlockCellName
        cell.ID = cell.name
        if content:
            # content.ID = cell.name hive.add_resource does it
            content._is_parsed = False  # It is necessary to parse it
            content.ID = cell.name  # It is edition, should have ID=BlockCellName
        r = Resource(cell, content)
        block_holder.add_resource(r)
        processor_changes.upsert(r.name, r.content, blob_changed=True)
    return processor_changes


def close_block(hive_holder, block_name):
    block_version = hive_holder[block_name].parent
    processor_changes = ProcessorChanges()
    _delete_block(hive_holder, block_name, processor_changes)
    _update_requirements(hive_holder, block_version, processor_changes)
    return processor_changes


def _delete_block(hive_holder, block_name, processor_changes):
    block_holder = hive_holder[block_name]
    for cell_name in block_holder.resources:
        processor_changes.delete(block_name + cell_name)
    hive_holder.delete_block(block_name)


def _update_requirements(hive_holder, new_version, processor_changes):
    for block_holder in hive_holder.block_holders:
        if new_version.block_name in block_holder.requirements:
            block_holder.requirements[new_version.block_name] = new_version
        new_reqs = block_holder.commit_config()
        if new_reqs:
            processor_changes.upsert(new_reqs.name, new_reqs.content, blob_changed=True)
