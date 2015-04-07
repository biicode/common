from unittest import TestCase
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.cmake_declaration import CMakeDeclaration


class TestCMakeDeclaration(TestCase):

    def test_no_matched_config_relpath(self):
        cut = CMakeDeclaration("../config")
        origin_block_cell_name = BlockCellName("fran/cmakeparsing/other/thing/start.cmake")

        block_cell_names = [BlockCellName("fran/cmakeparsing/CMakeLists.txt"),
                            BlockCellName("fran/cmakeparsing/other/thing/macro.cmake"),
                            BlockCellName("fran/cmakeparsing/config")]

        self.assertItemsEqual(set(), cut.match(block_cell_names, origin_block_cell_name))

    def test_matched_config_relpath(self):
        cut = CMakeDeclaration("config")
        origin_block_cell_name = BlockCellName("fran/cmakeparsing/configure/start.cmake")

        block_cell_names = [BlockCellName("fran/cmakeparsing/configure/start.cmake"),
                            BlockCellName("fran/cmakeparsing/other/thing/macro.cmake"),
                            BlockCellName("fran/cmakeparsing/configure/config"),
                            BlockCellName("fran/cmakeparsing/configure/config/other_config")]

        self.assertItemsEqual(set(["fran/cmakeparsing/configure/config"]),
                              cut.match(block_cell_names, origin_block_cell_name))

    def test_match_with_macro_cmake_relpath(self):
        cut = CMakeDeclaration("./cmake/Macros.cmake")
        origin_block_cell_name = BlockCellName("fran/cmakeparsing/CMakeLists.txt")

        block_cell_names = [BlockCellName("fran/cmakeparsing/CMakeLists.txt"),
                            BlockCellName("fran/cmakeparsing/cmake/Macros.cmake"),
                            BlockCellName("fran/cmakeparsing/cmake/Macros_2.cmake")]

        self.assertItemsEqual(set(["fran/cmakeparsing/cmake/Macros.cmake"]),
                              cut.match(block_cell_names, origin_block_cell_name))

    def test_match_with_macro_cmake_abspath(self):
        cut = CMakeDeclaration("fran/cmakeparsing/cmake/Macros_2.cmake")
        origin_block_cell_name = BlockCellName("fran/cmakeparsing/CMakeLists.txt")

        block_cell_names = [BlockCellName("fran/cmakeparsing/CMakeLists.txt"),
                            BlockCellName("fran/cmakeparsing/cmake/Macros.cmake"),
                            BlockCellName("fran/cmakeparsing/cmake/Macros_2.cmake")]

        self.assertItemsEqual(set(["fran/cmakeparsing/cmake/Macros_2.cmake"]),
                              cut.match(block_cell_names, origin_block_cell_name))
