from biicode.common.exception import BiiException
from biicode.common.diffmerge.compare import compare
from biicode.common.diffmerge.merge import SetThreeWayMerge
from biicode.common.model.blob import Blob
from biicode.common.diffmerge.text_merge import three_way_merge_text
from biicode.common.model.symbolic.block_version import BlockVersion


class BlobsMerger(SetThreeWayMerge):
    def merge_elements(self, common_blob, base_blob, other_blob):
        assert isinstance(base_blob, Blob)
        assert isinstance(other_blob, Blob)
        if base_blob.is_binary or other_blob.is_binary:
            self._biiout.warn("Can't merge binary contents, your file is keeped.")
            return base_blob, True

        common_text = None if common_blob is None else common_blob.bytes
        text, conflict = three_way_merge_text(common_text, base_blob.bytes, other_blob.bytes,
                                              self.base_name, self.other_name)
        return Blob(text), conflict


def update(block_holder, time, biiapi, biiout):
    block_name = block_holder.block_name
    parent = block_holder.parent
    if parent is None:
        raise BiiException('No parent info in block: %s' % block_name)

    biiout.info("Updating %s" % parent.to_pretty())
    if time is None:
        block_info = biiapi.get_block_info(parent.block)
        block_version = block_info.last_version
        time = block_version.time

    if time < parent.time:
        raise BiiException('Impossible to update block %s to an older version.\n'
                           'Current version %d > Requested version %d'
                           % (parent.block.to_pretty(), parent.time, time))

    # Tags for text merge
    base_tag_name = 'current'
    other_tag_name = 'v%d' % time

    # Prepare merge info
    base_resources = block_holder.resources
    other_version = BlockVersion(parent.block, time)

    common_holder = biiapi.get_block_holder(parent)
    common_holder.parent = parent
    common_holder.commit_config()
    common_resources = common_holder.resources

    if time == parent.time:  # For updating with self parent
        other_holder = common_holder
        common_resources = base_resources  # The common is the base, otherwise outdate
        other_renames = {}
    else:
        other_holder = biiapi.get_block_holder(other_version)
        other_holder.parent = parent
        other_holder.commit_config()
        other_renames = biiapi.get_renames(parent.block, parent.time, time)
    other_resources = other_holder.resources

    content_changes = compare(common_resources, base_resources)
    content_changes.deduce_renames()
    base_renames = content_changes.renames

    # Merge resources
    base_blobs = {name: content.load for name, (_, content) in base_resources.iteritems()
                  if content is not None}
    other_blobs = {name: content.load for name, (_, content) in other_resources.iteritems()
                   if content is not None}
    common_blobs = {name: content.load for name, (_, content) in common_resources.iteritems()
                    if content is not None}

    merger = BlobsMerger(base_tag_name, other_tag_name, biiout)
    result = merger.merge(base_blobs, other_blobs, common_blobs, base_renames, other_renames)

    final_result = {name: blob.load for name, blob in result.iteritems()}
    return final_result, other_version
