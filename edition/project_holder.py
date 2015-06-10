from collections import defaultdict
from biicode.common.find.finder_request import FinderRequest
from biicode.common.model.resource import Resource
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.symbolic.reference import ReferencedDependencies
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.symbolic.block_version import BlockVersion


class ProjectHolder(object):

    def __init__(self, dict_cells, dict_contents):
        self.hive_dependencies = None  # MUST BE ALWAYS BE ASSIGNED before usage
        self.settings = None
        resource_dict = defaultdict(list)
        for block_cell_name, cell in dict_cells.iteritems():
            content = dict_contents.get(block_cell_name)
            resource_dict[block_cell_name.block_name].append(Resource(cell, content))
        self._block_holders = {block_name: BlockHolder(block_name, resources)
                               for block_name, resources in resource_dict.iteritems()}

    def __repr__(self):
        result = []
        for bh in self.block_holders:
            result.append(repr(bh))
        return '\n'.join(result)

    def delete_empty_blocks(self):
        for block_name in self.blocks:
            if not self._block_holders[block_name].resources:
                del self._block_holders[block_name]

    def delete_block(self, block_name):
        del self._block_holders[block_name]

    @property
    def block_holders(self):
        return self._block_holders.itervalues()

    def __getitem__(self, key):
        return self._block_holders[key]

    def add_holder(self, block_holder):
        self._block_holders[block_holder.block_name] = block_holder

    @property
    def versions(self):
        """ given a set of block_names in edition (blocks folder), and a tracking BlockVersionTable
        return the current versions of such edition blocks, that is, time = None
        return: BlockVersionTable{ BlockName: BlockVersion time=None}
        """
        edition_versions = BlockVersionTable()
        for block_holder in self._block_holders.itervalues():
            parent = block_holder.parent
            edition_versions.add_version(BlockVersion(parent.block, None))
        return edition_versions

    @property
    def blocks(self):
        return set(self._block_holders.keys())

    @property
    def resources(self):
        result = {}
        for block_holder in self._block_holders.itervalues():
            for resource in block_holder.resources.itervalues():
                result[resource.name] = resource
        return result

    def find_request(self, policy):
        request = FinderRequest(policy)
        request.existing = self.external_dependencies()
        blocks = self.blocks
        # ONly those that have a block to be searched for
        unresolved = set()
        local_unresolved = set()
        for block_holder in self.block_holders:
            includes = block_holder.includes
            paths_size = len(block_holder.paths)
            for declaration in self.external_unresolved():
                try:
                    new_declaration, _ = declaration.prefix(includes, paths_size)
                except:
                    new_declaration = declaration
                decl_block = new_declaration.block()
                if decl_block and decl_block not in blocks:
                    unresolved.add(new_declaration)
                else:
                    local_unresolved.add(new_declaration)
        request.unresolved = unresolved
        request.block_names = self.blocks
        return request, local_unresolved

    def external_unresolved(self):
        unresolved = set()
        for block_holder in self.block_holders:
            unresolved.update(block_holder.unresolved())
        return unresolved

    def external_dependencies(self):
        result = ReferencedDependencies()
        blocks = self.blocks
        for block_holder in self.block_holders:
            dep_table = block_holder.requirements
            for block_name, version in dep_table.iteritems():
                if block_name not in blocks:
                    result[version]  # defaultdict will create empty item
            for resource in block_holder.simple_resources:
                cell = resource.cell
                for declaration in cell.dependencies.resolved:
                    targets = declaration.match(cell.dependencies.explicit)
                    if targets:
                        block = declaration.block()
                        if block not in blocks:
                            block_version = dep_table[block]
                            result[block_version][declaration].update(targets)
        return result
