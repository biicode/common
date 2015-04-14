from biicode.common.model.declare.cpp_declaration import Declaration
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.exception import BiiException
import os


class CMakeDeclaration(Declaration):
    """Represent a CMake Dependency declaration."""

    RELATIVE_DEPS = '../../deps/'

    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        """Return a set with block_cell_names that match with CMakeDeclaration.

        block_cell_names -> list containing all BCN to match against.
        origin_block_cell_name -> BCN that requires this CMakeDeclaration.

        There are three ways to solve this matching:
        1.Absolute path. ex: "fenix/math/Macros.cmake", "fenix/math/src_folder"
        2.Relative Path. ex: ".lib/parser/CMakeLists.txt" -> solve to abspath.

        Note: some includes could have the form "fenix\\block\\configure"
        """
        result = self._absolute_match(block_cell_names) or \
                 self._relative_match(block_cell_names, origin_block_cell_name)
        return result or set()

    def _absolute_match(self, block_cell_names):
        if self.RELATIVE_DEPS in self.name:
            self.name = self.name.split(self.RELATIVE_DEPS)[1]

        #Try absolute
        try:
            return self._to_block_cell_name(block_cell_names, self.name)
        except:
            pass

    def _relative_match(self, block_cell_names, origin_block_cell_name):
        if not origin_block_cell_name:
            return None
        #Try relative
        try:
            origin_dir_name = os.path.dirname(origin_block_cell_name)
            name = os.path.normpath(os.path.join(origin_dir_name, self.name))
            return self._to_block_cell_name(block_cell_names, name)
        except:
            pass

    def _to_block_cell_name(self, block_cell_names, name):
        brl = BlockCellName(name)
        if brl in block_cell_names:
            return set([brl])

    def block(self):
        try:
            return BlockCellName(self.name).block_name
        except:
            return None

    def match_system(self, system_cell_names):
        return set()

    def normalize(self, targets):
        if len(targets) != 1:
            raise BiiException("Incorrect input parameter %s" % targets)
        block_cell_name = iter(targets).next()
        if block_cell_name != self.name:
            return CMakeDeclaration(block_cell_name)
