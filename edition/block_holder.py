from biicode.common.model.cells import SimpleCell
from biicode.common.model.dependency_set import DependencySet
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.blob import Blob
from biicode.common.model.resource import Resource
from biicode.common.model.content import Content
from biicode.common.model.bii_type import TEXT
from biicode.common.edition.bii_config import BiiConfig
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.exception import ConfigurationFileError, BiiException


BIICODE_FILE = "biicode.conf"


class BlockHolder(object):

    def __init__(self, block_name, resources):
        """ resources is iterable of resources or dict {CellName: Resource(Cell, Content)}
        """
        assert isinstance(block_name, BlockName)
        self.block_name = block_name
        if isinstance(resources, dict):
            # we build the dict again to ensure the keys are CellName not BlockCellName
            self._resources = {r.cell_name: r for r in resources.itervalues()}
        else:
            self._resources = {r.cell_name: r for r in resources}
        self._simple_resources = None  # iterable (list) of simple resources

        # configuration files
        self._config = None

    @property
    def config(self):
        if self._config is None:
            try:
                res = self._resources[BIICODE_FILE]
                content = res.content.load.bytes
            except KeyError:
                content = None
            try:
                self._config = BiiConfig(content)
            except ConfigurationFileError as e:
                raise ConfigurationFileError('%s/biicode.conf: Line %s'
                                             % (self.block_name, str(e)))
        return self._config

    @property
    def mains(self):
        return self.config.mains

    @property
    def tests(self):
        return self.config.tests

    @property
    def data(self):
        return self.config.data

    @property
    def paths(self):
        return self.config.paths

    @property
    def dependencies(self):
        return self.config.dependencies

    @property
    def requirements(self):
        return self.config.requirements

    @property
    def parent(self):
        if self.config.parent:
            if self.config.parent.block_name != self.block_name:
                raise BiiException("A block should have same BlockName as it's parent.\n"
                                   "%s's parent is %s"
                                   % (self.block_name, self.config.parent.block_name))

            return self.config.parent
        return self.block_name.init_version()

    @property
    def includes(self):
        return self.config.includes

    @requirements.setter
    def requirements(self, block_version_table):
        assert isinstance(block_version_table, BlockVersionTable)
        self.config.requirements = block_version_table

    @parent.setter
    def parent(self, parent):
        """ Should be called only after publish and open
        """
        assert isinstance(parent, BlockVersion)
        self.config.parent = parent

    def commit_config(self):
        '''
        Returns:
            None if the config file didnt change. The config file Resource in case
            it was created or modified
        '''

        new_content = self.config.dumps()
        if new_content:
            name = self.block_name + BIICODE_FILE
            new_res = Resource(SimpleCell(name, TEXT),
                               Content(name, load=Blob(new_content), created=True))
            self.add_resource(new_res)
            return new_res
        return None

    @property
    def cell_names(self):
        """ return CellNames
        """
        return set(self._resources.keys())

    @property
    def block_cell_names(self):
        """ return BlockCellNames
        """
        return {self.block_name + name for name in self._resources}

    def __getitem__(self, key):
        return self._resources[key]

    @property
    def simple_resources(self):
        ''' Useful as most iterations are done over simple resources.
        If a block_name is given, the method returns only it's simple resources
        '''
        if self._simple_resources is None:
            self._simple_resources = [x for x in self._resources.itervalues()
                                      if isinstance(x.cell, SimpleCell)]
        return self._simple_resources

    @property
    def resources(self):
        return self._resources

    def add_resource(self, resource):
        self._resources[resource.cell_name] = resource
        self._simple_resources = None

    def delete_resource(self, name):
        del self._resources[name]
        self._simple_resources = None

    def external_targets(self):
        '''return: a set(BlockCellNames) with cells not included'''
        return self._filter(lambda x, y: x != y)

    def internal_targets(self):
        '''return the internal targets as set(BlockCellNames) of dependencies
        of resources with "names" (NOT EXTERNAL) '''
        return self._filter(lambda x, y: x == y)

    def _filter(self, compare):
        result = set()
        for resource in self.simple_resources:
            cell = resource.cell
            for target in cell.dependencies.targets:
                if compare(target.block_name, self.block_name):
                    result.add(target)
        return result

    def unresolved(self):
        result = set()
        for cell, _ in self.simple_resources:
            result.update(cell.dependencies.unresolved)
        return result

    def translate_virtuals(self, block_cell_names):
        '''Handles pointing to virtual targets instead contained ones'''
        result = set()
        for block_cell_name in block_cell_names:
            assert block_cell_name.block_name == self.block_name, "%s != %s" % (block_cell_name,
                                                                                self.block_name)
            cell = self._resources[block_cell_name.cell_name].cell
            try:
                target = cell.container or cell.name
            except AttributeError:
                target = cell.name
            result.add(target)
        return result

    def deps(self, files=None):
        deps = DependencySet()
        for name, (cell, _) in self._resources.iteritems():
            if files is None or self.block_name + name in files:
                if isinstance(cell, SimpleCell):
                    deps.update(cell.dependencies)
        return deps
