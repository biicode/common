from biicode.common.diffmerge.changes import Changes, Modification
from biicode.common.model.resource import resource_diff_function


def diff(biiapi, block_holder=None, v1=None, v2=None):
    if v1 and v2:  # comparison between two remotes
        changes = compare_remote_versions(biiapi, v1, v2)
    else:
        if not v1:
            v1 = block_holder.parent
        if v1.time == -1:
            changes = compare({}, block_holder.resources)
        else:
            other_block_holder = biiapi.get_block_holder(v1)
            # Filter parent modification
            other_block_holder.parent = v1
            #other_block_holder.commit_config()
            changes = compare(other_block_holder.resources, block_holder.resources)
            changes.deduce_renames()

    from biicode.common.diffmerge.differ import compute_diff
    return compute_diff(changes, resource_diff_function)


def compare(base_resources, other_resources):
    """Generic compare items and return a Changes object.
    base_resources and other_resources can be any dict {ID: Value}"""

    changes = Changes()
    if base_resources is None:
        base_resources = {}

    # Check for deleted & modified, when modified keeps other
    for key, value in base_resources.iteritems():
        other_value = other_resources.get(key)
        if other_value is None:
            changes.deleted[key] = value
        elif other_value != value:
            changes.modified[key] = Modification(value, other_value)

    # check for created
    for key, value in other_resources.iteritems():
        if key not in base_resources:
            changes.created[key] = value

    return changes


def compare_remote_versions(biiapi, base_version, other_version):
    '''To compare one version against other, they should be versions, computing the DIFF
    If there is a path between them the renames is read from biiapi. Otherwise is deduced from
    changes object.

    base_version: BlockVersion
    other_version: BlockVersion
    '''
    block_holder_base = biiapi.get_block_holder(base_version)
    block_holder_other = biiapi.get_block_holder(other_version)
    changes = compare(block_holder_base.resources, block_holder_other.resources)

    if base_version.block == other_version.block:
        renames = biiapi.get_renames(base_version.block, base_version.time, other_version.time)
        changes.renames = renames
    else:
        changes.deduce_renames()
    return changes
