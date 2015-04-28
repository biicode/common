from biicode.common.model.cells import SimpleCell, VirtualCell
from biicode.common.model.symbolic.reference import References
from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.deps.closure import Closure
from collections import namedtuple
from biicode.common.deps.block_version_graph_builder import compute_effective
from collections import defaultdict
from biicode.common.exception import ConfigurationFileError, BiiException
import re


IMPLICIT_DEPENDENCIES = re.compile("readme*|CMakeLists.txt|license*|bii_deps_config.cmake|biicode.conf")


def build_closure(biiapi, references, base_table, settings=None, biiout=None):
    graph = BlockVersionGraph()
    closure = Closure()
    visited = set()
    visited_block_versions = set()
    overwrites = defaultdict(set)
    if references:
        assert not ([r for r in references.explode() if r.block_version.block_name in base_table
                     and base_table[r.block_version.block_name] != r.block_version])
        frontier = [(references, base_table)]  # Of tuple (references, base_table)
    else:
        frontier = []

    class Visited(namedtuple('Visited', 'version cell_name, dep_table')):
        def __hash__(self):
            return hash((self.version, self.cell_name))

    while frontier:
        references, base_table = frontier.pop()
        retrieved = biiapi.get_published_resources(references)
        for block_version, resources in retrieved.iteritems():
            graph.add_node(block_version)
            dep_targets = set()

            if block_version not in visited_block_versions:
                cell_names = biiapi.get_cells_snapshot(block_version)
                _add_implicit_targets(dep_targets, cell_names, block_version)
                visited_block_versions.add(block_version)
            try:
                up_table = biiapi.get_dep_table(block_version)
            except Exception as e:
                raise BiiException('%s\nbiicode needs compare your local "%s" block with your last'
                                   ' version published one. If you want to delete it, delete the '
                                   'folder in the filesystem.' % (str(e),
                                                                  block_version.block_name))
            effective, propagate, overwrite = compute_effective(base_table, up_table,
                                                                block_version.block_name)
            if overwrite:
                overwrites[block_version].update(overwrite)

            for cell_name, resource in resources.iteritems():
                closure.add_item(resource, block_version, biiout)
                visited.add(Visited(block_version, cell_name, base_table))
                _update_dep_targets(dep_targets, resource, settings, biiout)

            other_refs = References()
            self_refs = References()
            for target in dep_targets:
                if target.block_name == block_version.block_name:
                    next_visit = Visited(block_version, target.cell_name, base_table)
                    if next_visit not in visited:
                        self_refs[block_version].add(target.cell_name)
                else:
                    next_version = effective[target.block_name]
                    graph.add_edge(block_version, next_version)
                    if next_version.time is not None:
                        next_visit = Visited(next_version, target.cell_name, propagate)
                        if next_visit not in visited:
                            other_refs[next_version].add(target.cell_name)

            if other_refs:
                frontier.append((other_refs, propagate))
            if self_refs:
                frontier.append((self_refs, base_table))

    return graph, closure, overwrites


def _add_implicit_targets(dep_targets, cell_names, block_version):
    for cell in cell_names:
        if IMPLICIT_DEPENDENCIES.match(cell):
            dep_targets.add(block_version.block_name + cell)


def _update_dep_targets(dep_targets, resource, settings, biiout):
    cell = resource.cell
    if isinstance(cell, SimpleCell):
        dep_targets.update(cell.dependencies.targets)
    else:  # virtual
        assert isinstance(cell, VirtualCell)
        if settings:
            try:
                dep_targets.update([cell.evaluate(settings)])
            except ConfigurationFileError as e:
                biiout.error("Error evaluating virtual %s: %s" % (cell.name, e.message))
        else:
            dep_targets.update(cell.resource_leaves)
