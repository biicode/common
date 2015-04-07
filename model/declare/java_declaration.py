from biicode.common.utils.bii_logging import logger
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.exception import BiiException
import os
import re
from biicode.common.model.declare.declaration import Declaration
from biicode.common.model.brl.system_cell_name import SystemCellName


def normalized_name(name):
    """ Translate from java import name to path.

    :param name: str module name. biicode.common.edition
    :return: str. biicode/common/edition.java
    """
    return "%s.java" % name.replace('.', '/')


class JavaDeclaration(Declaration):

    def __init__(self, name):
        """ The name of the dependency, initially what the user types "com.biicode.Class"
        The Case is stored as typed by the user, no changes until it is found and managed by biicode
        """
        assert not '/' in name
        assert not '.java' in name
        Declaration.__init__(self, name)

    @property
    def normalizedName(self):
        return self.name.replace('\\', '/')

    def extension_namelist(self):
        name_file = self.name.replace('.', '/')
        name_file_import = name_file.replace('.java', '')
        #name_file_import = name_file_import.replace('.', '/')
        self.extension_name = [self.name, name_file, name_file + '.java', name_file_import]

    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        #Try absolute
        bcn = self._block_cell_name()
        if bcn in block_cell_names:
            return set([bcn])

        #Try relative
        try:
            self.extension_namelist()
            for name in self.extension_name:
                name_ext = os.path.normpath(os.path.join(os.path.dirname(origin_block_cell_name),
                                                         name))
                brl = BlockCellName(name_ext)
                if brl in block_cell_names:
                    return set([brl])
        except:
            pass

        # Try APPROXIMATE, only in same block
        if origin_block_cell_name:
            try:
                block_name = origin_block_cell_name.block_name
                normalized_include = self.normalizedName
                result = set()
                for name in block_cell_names:
                    if name.block_name == block_name:  # Approximate only find in same Block
                        if name.endswith(normalized_include):
                            tail = os.path.split(name)[1]
                            if len(normalized_include) >= len(tail):
                                result.add(name)

                if len(result) == 1:
                    return result

                #TODO: Inform user of multiple matchs
                logger.info("Matchs for name %s are %s" % (self.name, result))
            except Exception as e:
                logger.error("Approximate find failed %s" % str(e))
                pass

        return set()

    def match_system(self, system_cell_names):
        self.extension_namelist()
        bcn = self._block_cell_name()
        if not bcn:
            bcn = self.name.replace('.', '/') + '.java'
        name = SystemCellName(bcn)
        if name in system_cell_names:
            return set([name])
        return set()

    def block(self):
        try:
            return self._block_cell_name().block_name
        except:
            return None

    def _block_cell_name(self):
        try:
            return BlockCellName(normalized_name(self.name))
        except:
            return None

    def normalize(self, targets):
        if len(targets) != 1:
            raise BiiException("Incorrect input parameter %s" % targets)
        block_cell_name = iter(targets).next()
        declaration = block_cell_name.replace("/", ".")
        java_extension_re = re.compile("\.java$")
        declaration = java_extension_re.sub('', declaration)
        return JavaDeclaration(declaration)
