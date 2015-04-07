import os
import re
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.declare.declaration import Declaration
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.exception import InvalidNameException


def is_relative(name):
    return name.startswith('./') or name.startswith("../")


class NodeDeclaration(Declaration):
    """Represent NodeJs Dependency declaration."""

    EXTENSION_REGEX = re.compile(r".*\.(js|json|node)$")

    ENTRY_POINT_NAMES = ['index.js', 'package.json']

    def __init__(self, name):
        super(NodeDeclaration, self).__init__(name)
        self._extension_name = self.extension_namelist()

    def extension_namelist(self):
        """
        Return a list with all possible node extensions
        if cell name doesn't have a valid sufix.
        """
        name_list = [self.name]
        if not self.EXTENSION_REGEX.match(self.name):
            name_list = [self.name + '.js', self.name + '.node', self.name + '.json']
        return name_list

    def _absolute_match(self, block_cell_names, origin_block_cell_name=None):
        try:
            for name in self._extension_name:
                brl = BlockCellName(name)
                if brl in block_cell_names:
                    return set([brl])
        except InvalidNameException:
            pass

    def _relative_match(self, block_cell_names, origin_block_cell_name=None):
        if not origin_block_cell_name or not self.name.startswith('.'):
            return
        try:
            for name in self._extension_name:
                dname = os.path.dirname(origin_block_cell_name)
                name_ext = os.path.normpath(os.path.join(dname, name))
                brl = BlockCellName(name_ext)
                if brl in block_cell_names:
                    return set([brl])
        except (InvalidNameException, AttributeError):
            pass

    def _index_match(self, block_cell_names, origin_block_cell_name=None):
        result = set()
        #absolute index match
        for block_cell_name in block_cell_names:
            if block_cell_name.block_name == self.block():
                if block_cell_name.cell_name in self.ENTRY_POINT_NAMES:
                    result.add(block_cell_name)
        # Relative index match
        if origin_block_cell_name:
            dname = os.path.dirname(origin_block_cell_name)
            name_ext = os.path.normpath(os.path.join(dname, 'index.js'))
            block_cell_name = BlockCellName(name_ext)
            if block_cell_name in block_cell_names:
                result.add(block_cell_name)
        return result

    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        """Return a set with block_cell_names that match with NodeDeclaration.


        block_cell_names -> list containing all BCN to match against.
        origin_block_cell_name -> BCN that requires this NodeDeclaration.

        There are three ways to solve this matching:
        1.Absolute path. ex: "fran/noderedis/client.js"
        2.Relative Path. ex: ".lib/parser/hiredis.js" -> solve to abspath.
        4.index.js or package.json as node convention. ex: "fran/noderedis"

        """
        match_methods = [self._absolute_match,
                         self._relative_match,
                         self._index_match]

        for match_method in match_methods:
            result = match_method(block_cell_names, origin_block_cell_name)
            if result:
                return result

        return set()

    def match_system(self, system_cell_names):
        """Return if this declaration is a system dep."""
        for name in self._extension_name:
            name = SystemCellName(name)
            if name in system_cell_names:
                return set([name])
        return set()

    def block(self):
        """Return block name as string.

        There are three kinds of NodeDeclaration:
        1. abspath fran/noderedis/client.js
        2. relpath with block fran/noderedis
        3. relpath without block ./

        """
        try:
            return BlockCellName(self.name).block_name
        except (InvalidNameException):
            try:
                return BlockName(self.name)
            except (InvalidNameException):
                return None

    def block_cell_name(self):
        """Return BlockCellName only if it's possible."""
        try:
            return BlockCellName(self.name)
        except InvalidNameException:
            return None

    def normalize(self, targets):
        """Return normalized declaration to absolute path as biicode convention.

        If declaration is a node module declaration like fran/redis or
        relative path it returns same declaration.

        """
        # relative name is not changed
        block_cell_name = iter(targets).next()
        if is_relative(self.name) or block_cell_name.cell_name in self.ENTRY_POINT_NAMES:
            return NodeDeclaration(self.name.lower())
        # absolute, external name, can be changed
        if block_cell_name != self.name:
            return NodeDeclaration(block_cell_name)

    @property
    def normalizedName(self):
        return self.name.lower().replace('\\', '/')
