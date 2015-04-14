from unittest import TestCase
from biicode.common.model.bii_type import BiiType, PYTHON
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.python_declaration import PythonDeclaration, PythonImport
from biicode.common.dev.system_resource_validator import getSystemNameValidatorFor
from mock import Mock


class TestPythonDeclaration(TestCase):

    def test_from_import_block(self):
        sut = PythonDeclaration("from biicode.common.edition import Parser")
        self.assertEquals("biicode/common", sut.block())
        self.assertEquals([('Parser', None)], sut.python_import().names)

    def test_general_import_block(self):
        sut = PythonDeclaration("import biicode.common.edition")
        self.assertEquals("biicode/common", sut.block())
        self.assertEquals(None, sut.python_import().names)

    def test_from_import_all(self):
        sut = PythonDeclaration("from biicode.common.edition import *")
        self.assertEquals("biicode/common", sut.block())
        self.assertEquals([("*", None)], sut.python_import().names)

    def test_aliased_general_import_block(self):
        sut = PythonDeclaration("import biicode.common.edition as pepe")
        self.assertEquals("biicode/common", sut.block())
        self.assertEquals(None, sut.python_import().names)

    def test_aliased_from_import_block(self):
        sut = PythonDeclaration("from biicode.common.edition import Parser as pepe")
        self.assertEquals("biicode/common", sut.block())
        self.assertEquals([("Parser", "pepe")], sut.python_import().names)

    def test_multi_aliased_from_import_block(self):
        sut = PythonDeclaration("from biicode.common.edition import Parser as pepe, Counter as cont")
        self.assertEquals("biicode/common", sut.block())
        self.assertEquals([("Parser", "pepe"), ("Counter", "cont")], sut.python_import().names)

    def test_from_import_error(self):
        sut = PythonDeclaration("from biicode.common.edition impor Parser")
        self.assertIsNone(sut.block())

    def test_simple_match(self):
        sut = PythonDeclaration("import biicode.common.edition")
        block_cell_names = set([BlockCellName("biicode/common/edition.py"),
                                BlockCellName("biicode/common/jarl.py")])
        self.assertEquals(set([BlockCellName("biicode/common/edition.py")]),
                          sut.match(block_cell_names))

    def test_init_match(self):
        sut = PythonDeclaration("import biicode.common.edition")
        block_cell_names = set([BlockCellName("biicode/common/__init__.py"),
                                BlockCellName("biicode/common/edition.py")])
        self.assertEquals(block_cell_names, sut.match(block_cell_names))

    def test_multi_init_match(self):
        sut = PythonDeclaration("import biicode.common.edition")
        block_cell_names = set([BlockCellName("biicode/common/__init__.py"),
                                BlockCellName("biicode/common/test/__init__.py"),
                                BlockCellName("biicode/common/edition.py")])
        expected = set([BlockCellName("biicode/common/__init__.py"),
                        BlockCellName("biicode/common/edition.py")])
        self.assertEquals(expected, sut.match(block_cell_names))

    def test_multi_init_levels_match(self):
        sut = PythonDeclaration("import biicode.common.test.name")
        block_cell_names = set([BlockCellName("biicode/common/__init__.py"),
                                BlockCellName("biicode/common/test/__init__.py"),
                                BlockCellName("biicode/common/test/name.py"),
                                BlockCellName("biicode/common/edition.py")])

        expected = set([BlockCellName("biicode/common/__init__.py"),
                        BlockCellName("biicode/common/test/__init__.py"),
                        BlockCellName("biicode/common/test/name.py")])
        self.assertEquals(expected, sut.match(block_cell_names))

    def test_multi_init_levels_match_relative_import(self):
        sut = PythonDeclaration("import name")

        block_cell_names = set([BlockCellName("biicode/common/__init__.py"),
                                BlockCellName("biicode/common/test/__init__.py"),
                                BlockCellName("biicode/common/test/name.py"),
                                BlockCellName("biicode/common/edition.py")])

        expected = set([BlockCellName("biicode/common/__init__.py"),
                        BlockCellName("biicode/common/test/__init__.py"),
                        BlockCellName("biicode/common/test/name.py")])

        self.assertEquals(expected, sut.match(block_cell_names,
                                              BlockCellName("biicode/common/test/name.py")))

    def test_simple_match_relative(self):
        sut = PythonDeclaration("from edition import *")

        block_cell_names = set([BlockCellName("biicode/common/edition.py"),
                                BlockCellName("biicode/common/jarl.py")])

        from_block_cell_name = BlockCellName("biicode/common/main.py")
        self.assertEquals(set([BlockCellName("biicode/common/edition.py")]),
                          sut.match(block_cell_names, from_block_cell_name))

    def test_simple_match_relative_in_different_block(self):
        sut = PythonDeclaration("from edition import *")

        block_cell_names = set([BlockCellName("biicode/parsing/edition.py"),
                                BlockCellName("biicode/parsing/jarl.py")])

        from_block_cell_name = BlockCellName("biicode/common/main.py")
        self.assertEquals(set(),
                          sut.match(block_cell_names, from_block_cell_name))

    def test_match_system(self):
        sut = PythonDeclaration("import re")
        validator = self.generate_python_sys_libs()
        self.assertEquals(set(["re.py"]), sut.match_system(validator))

    def test_match_composed_system(self):
        sut = PythonDeclaration("import xml.dom.domreg")
        validator = self.generate_python_sys_libs()
        self.assertEquals(set(["xml/dom/domreg.py"]), sut.match_system(validator))

    def test_match_system_inexistent(self):
        sut = PythonDeclaration("import reee")
        validator = self.generate_python_sys_libs()
        self.assertEquals(set([]), sut.match_system(validator))

    def generate_python_sys_libs(self):
        cell_mock = Mock()
        cell_mock.type = BiiType(PYTHON)
        validator = getSystemNameValidatorFor(cell_mock).names()
        return validator

    def test_normalize(self):
        sut = PythonDeclaration("import myblock")
        result = sut.normalize(['testuser/block/__init__.py', 'testuser/block/myblock.py'])
        self.assertEquals(PythonDeclaration("import testuser.block.myblock as myblock"), result)

    def test_normalize_multi_dir(self):
        sut = PythonDeclaration("import biipyc")
        result = sut.normalize(['testuser1/pyc/pythondynlibs/biipyc.py'])
        self.assertEquals(PythonDeclaration("import testuser1.pyc.pythondynlibs.biipyc as biipyc"),
                          result)

    def test_normalize_import_with_alias(self):
        sut = PythonDeclaration("import myblock as block")
        result = sut.normalize(['testuser/block/__init__.py', 'testuser/block/myblock.py'])
        self.assertEquals(PythonDeclaration("import testuser.block.myblock as block"), result)

    def test_complex_normalize(self):
        sut = PythonDeclaration("from myblock import Parser, Runner")
        result = sut.normalize(['testuser/block/__init__.py', 'testuser/block/myblock.py'])
        self.assertEquals(PythonDeclaration("from testuser.block.myblock import Parser, Runner"),
                          result)

    def test_complex_normalize_with_alias(self):
        sut = PythonDeclaration("from myblock import Parser as Hell")
        result = sut.normalize(['testuser/block/__init__.py', 'testuser/block/myblock.py'])
        self.assertEquals(PythonDeclaration("from testuser.block.myblock import Parser as Hell"),
                          result)

    def test_normalize_composed_import(self):
        sut = PythonDeclaration("import     biicode.common.edition.parsing")
        result = sut.normalize(['biicode/common/edition/parsing.py'])
        self.assertEquals(PythonDeclaration("import biicode.common.edition.parsing"), result)

    def test_python_import(self):
        from_import = "from biicode.common.edition import Parser"
        parsed_import = PythonImport.parse(from_import)
        self.assertEquals(PythonImport(module="biicode.common.edition", names=[("Parser", None)]),
                          parsed_import)
        self.assertEquals(from_import, parsed_import.to_python_statement())
