import os
from biicode.common.exception import BiiException
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.declaration import Declaration
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.exception import InvalidNameException
import fnmatch


class CPPDeclaration(Declaration):

    RELATIVE_DEPS = '../../deps/'

    def prefix(self, mapping, paths_size):
        for i, (pattern, path) in enumerate(mapping):
            if fnmatch.fnmatch(self.name, pattern):
                new_declaration = CPPDeclaration(path + '/' + self.name)
                new_declaration.properties = self.properties
                return new_declaration, (paths_size + i, path)

    def _paths_match(self, block_cell_names, paths):
        # This is relative too
        if not paths:
            return
        block_name = next(iter(block_cell_names)).block_name
        for i, path in enumerate(paths):
            try:
                tmp_path = '%s/%s/%s' % (block_name, path, self.name)
                # If path is "/" will be converter to right path removing double //
                # It fixes "\" paths too
                tmp_path = os.path.normpath(tmp_path)
                brl = BlockCellName(tmp_path)
                if brl in block_cell_names:
                    self.path = (i, block_name + path)  # TODO: Improve this pattern
                    return {brl}
            except InvalidNameException:
                pass

    def _absolute_match(self, block_cell_names):
        if self.RELATIVE_DEPS in self.name:
            self.name = self.name.split(self.RELATIVE_DEPS)[1]

        #Try absolute
        try:
            brl = BlockCellName(self.name)
            if brl in block_cell_names:
                return set([brl])
        except InvalidNameException:
            pass

    def _relative_match(self, block_cell_names, origin_block_cell_name):
        if not origin_block_cell_name:
            return None
        #Try relative
        try:
            origin_dir_name = os.path.dirname(origin_block_cell_name)
            name = os.path.normpath(os.path.join(origin_dir_name, self.name))
            brl = BlockCellName(name)
            if brl in block_cell_names:
                return set([brl])
        except (InvalidNameException, AttributeError):
            pass

    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        """Return a set with block_cell_names that match with CPPDeclaration.


        block_cell_names -> list containing all BCN to match against.
        origin_block_cell_name -> BCN that requires this CPPDeclaration.
        paths -> Paths to look into (from paths.bii)

        There are three ways to solve this matching:
        1.Absolute path. ex: "fran/test/sphere.h" or "../../deps/akka/math/a.h"
        2.Relative Path. ex: ".lib/parser/parser.h" -> solve to abspath.

        """
        result = (self._absolute_match(block_cell_names) or
                  self._relative_match(block_cell_names, origin_block_cell_name) or
                  self._paths_match(block_cell_names, paths))

        return result or set()

    def match_system(self, system_cell_names):
        name = SystemCellName(self.name)
        if name in system_cell_names:
            return set([name])
        return set()

    def block(self):
        try:
            return BlockCellName(self.name).block_name
        except:
            return None

    def normalize(self, targets):
        if len(targets) != 1:
            raise BiiException("Incorrect input parameter %s" % targets)
        block_cell_name = iter(targets).next()
        if block_cell_name != self.name:
            return CPPDeclaration(block_cell_name)
