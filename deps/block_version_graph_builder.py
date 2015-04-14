from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.exception import NotFoundException
from biicode.common.exception import NotInStoreException
from collections import defaultdict


def compute_effective(base_table, current_table, current_block_name):
    """ compute the effective BlockVersionTable for dependencies.
    param base_table: Propagate block version table computed so far
    param current_table: the actual BlockVersionTable as stored in model (DB)
    param current_block_name: the actual BlockName, to be discarded in the computation
    return: (effective BlockVersionTable: The actual values of dependencies for this block,
            propagate BlockVersionTable: Values of dependencies to be moved up in the tree,
            overwrites set(BlockVersion): versions that superseed current_table values
    """
    # self.copy() does not work, creates plain dict
    effective = current_table.copy()
    propagate = current_table.copy()
    overwrites = set()
    for name, version in base_table.iteritems():
        if name == current_block_name:
            continue
        old_version = current_table.get(name)
        if old_version and old_version != version:
            overwrites.add(version)
        propagate[name] = version
        if name in effective:
            effective[name] = version
    return effective, propagate, overwrites


def block_version_graph_build(get_dep_table, base_versions, base_table):
    graph = BlockVersionGraph()
    overwrites = defaultdict(set)
    for version in base_versions:
        _recursive_block_version_graph_build(get_dep_table, graph, version, base_table, overwrites)
    return graph, overwrites


def _recursive_block_version_graph_build(get_dep_table, graph, version, base_table, overwrites):
    try:
        cur_table = get_dep_table(version)
        graph.add_node(version)
        effective, propagate, overwr = compute_effective(base_table, cur_table, version.block_name)
        if overwr:
            overwrites[version].update(overwr)
    except (NotInStoreException, NotFoundException):
        return

    for dep_version in effective.itervalues():
        if dep_version != version:
            graph.add_edge(version, dep_version)

    for dep_version in effective.itervalues():
        _recursive_block_version_graph_build(get_dep_table, graph, dep_version, propagate,
                                            overwrites)
