import re
from biicode.common.edition.parsing.python.python_import import PythonImport
from biicode.common.exception import InvalidNameException
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.utils.bii_logging import logger
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.declaration import Declaration
import os


def normalized_name(name):
    """ Translate from python module name to path.

    :param name: str module name. biicode.common.edition
    :return: str. biicode/common/edition.py
    """
    return "%s.py" % name.replace('.', '/')


class PythonDeclaration(Declaration):

    def __init__(self, name):
        """ The name of the dependency, initially what the user types "import block.module.Class"
        The Case is stored as typed by the user, no changes until it is found and managed by biicode
        """
        assert not '/' in name
        Declaration.__init__(self, name)

    def python_import(self):
        try:
            return self._python_import
        except AttributeError:
            self._python_import = PythonImport.parse(self.name)
            return self._python_import

    def block(self):
        python_import = self.python_import()
        try:
            return BlockCellName(normalized_name(python_import.module)).block_name
        except:
            return None

    def match_system(self, system_cell_names):
        python_import = self.python_import()
        name = SystemCellName(normalized_name(python_import.module))
        if name in system_cell_names:
            return set([name])
        return set()

    def _is_python_package(self, block_cell_name, other_bcell_name):
        """Check if other should be added as dependency to cell in cases that other
            is __init__.py.
        """
        level_cell_path = len(block_cell_name.split('/')[:-1])
        level_other_path = len(other_bcell_name.split('/')[:-1])
        return all([block_cell_name.block_name == other_bcell_name.block_name,
               other_bcell_name.endswith("__init__.py"),
               level_cell_path >= level_other_path])

    def collect_init_dependencies(self, block_cell_name, block_cell_names, result):
        for bcn in block_cell_names:
            if self._is_python_package(block_cell_name, bcn):
                result.add(bcn)

    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        result = self._absolute_match(block_cell_names)
        if len(result) > 0:
            return result
        return self._relative_match(block_cell_names, origin_block_cell_name)

    def _absolute_match(self, block_cell_names):
        python_import = self.python_import()
        result = set()
        try:
            bcn = BlockCellName(normalized_name(python_import.module))
            if bcn in block_cell_names:
                self.collect_init_dependencies(bcn, block_cell_names, result)
                result.add(bcn)
        except InvalidNameException:
            # In relative imports like import model
            # BlockCellName raises an exception.
            pass
        return result

    def _relative_match(self, block_cell_names, from_block_cell_name):
        ''' When import is relative the followed approach is
        Look for files within same block to match with import.
        '''
        python_import = self.python_import()
        result = set()
        if from_block_cell_name:
            try:
                block_name = from_block_cell_name.block_name
                normalized_import = normalized_name(python_import.module)

                for block_cell_name in [bcn for bcn in block_cell_names
                                        if bcn.block_name == block_name
                                        and bcn.endswith(normalized_import)]:
                    tail = os.path.split(block_cell_name)[1]
                    if len(normalized_import) >= len(tail):
                        # To avoid match like test.py pretest.py
                        result.add(block_cell_name)
                        self.collect_init_dependencies(block_cell_name, block_cell_names, result)

                return result
            except Exception as e:
                logger.error("Approximate find failed %s" % str(e))
                pass
        return set()

    def normalize(self, targets):
        """Return a normalized PythonDeclaration, transforming
           from relative imports to absolute imports.
            :param targets: list of filenames. Including __init__.py files.
        """
        for target in targets:
            if "__init__.py" not in target:
                declaration = target

        declaration = declaration.replace("/", ".")
        python_extension_re = re.compile("\.py$")
        declaration = python_extension_re.sub('', declaration)

        original_import = self.python_import()

        alias = original_import.alias
        if original_import.is_aliasable():
            alias = original_import.module

        updated_import = PythonImport(module=declaration, names=original_import.names, alias=alias)
        return PythonDeclaration(updated_import.to_python_statement())

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)
