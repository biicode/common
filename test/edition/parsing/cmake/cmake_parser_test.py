import unittest
from biicode.common.edition.parsing.cmake.cmake_parser import CMakeParser
from nose.plugins.attrib import attr


cmake_text = r'''# This CMakeLists.txt file helps defining your block building and compiling
# Include the main biicode macros and functions
# To learn more about the CMake use with biicode, visit http://docs.biicode.com/c++/building.html
# Or check the examples below


# Initializes block variables
INIT_BIICODE_BLOCK()
# This function creates the following variables:
#     ${BII_BLOCK_NAME}       The name of the current block (e.g. "box2d")
#     ${BII_BLOCK_USER}       The user's name (e.g. "phil")
#     ${BII_BLOCK_PREFIX}     The directory where the block is located (blocks or deps)

# Also it loads variables from the cmake/bii_user_block_vars.cmake
#     ${BII_CREATE_LIB}       TRUE if you want to create the library
#     ${BII_LIB_SRC}          File list to create the library
#     ${BII_LIB_TYPE}         STATIC(default) or SHARED
#     ${BII_LIB_DATA_FILES}   Data files that have to be copied to bin
#     ${BII_LIB_DEPS}         Dependencies to other libraries (user2_block2, user3_blockX)
#     ${BII_LIB_SYSTEM_DEPS}  System linking requirements as winmm, m, ws32, pthread...

# You can use or modify them here, for example, to add or remove files from targets based on OS
# Or use typical cmake configurations done BEFORE defining targets. Examples:
#     ADD_DEFINITIONS(-DFOO)
#     FIND_PACKAGE(OpenGL QUIET)
#     BII_FILTER_LIB_SRC(${BII_LIB_SRC})
#     You can add INCLUDE_DIRECTORIES here too

set (MY_NEW        "testings")
set(other ${MY_NEW})

# Actually create targets: EXEcutables and libraries.
include(

    "src/Macros.cmake"

    )

            INCLUDE( src2/Macros2.cmake)
      INCLUDE( src3\\Macros3.cmake )
add_subdirectory(                        "include")


#     INCLUDE( src2/Macros2.cmake)
#    INCLUDE( src3\\Macros3.cmake )
#    add_subdirectory("include")

MESSAGE("-------------> MACROO -----> ${MY_MACRO}")
MESSAGE("-------------> MACROO 2 -----> ${MY_MACRO2}")
MESSAGE("-------------> MACROO 3 -----> ${MY_MACRO3}")

conFigure_File( config/Config include/config.h )

ADD_BIICODE_TARGETS()
# This function creates the following variables:
#     ${BII_BLOCK_TARGETS} List of targets defined in this block
#     ${BII_LIB_TARGET}  Target library name, usually in the form "user_block"
#     ${BII_exe_name_TARGET}: Executable target (e.g. ${BII_main_TARGET}. You can also use
#                            directly the name of the executable target (e.g. user_block_main)
'''

cmake_includes_text = r'''            INCLUDE("src/Macros.cmake")
      include( src2\\Macros2.cmake )
      # My comment
InClUDE(
    ${My_secret_Var}/Macros2.cmake
    )
#      iNCLUDe(
#      src4\\Macros4.cmake )
 include ( Module/cmake/Macro)
'''

cmake_add_subdirectory_text = r'''            add_Subdirectory("${src}")
      add_subdirectory(cmake)
      # My comment
ADD_Subdirectory(
    ${My_secret_Var}
    )
      ADD_SubdirectorY(
      'src4' )
'''

cmake_configure_file_text = r'''conFigure_File("src/Macros.cmake")
  configure_file(config.h.in "${CMAKE_CURRENT_BINARY_DIR}/config.h" @ONLY)
      # My comment
conFigure_File(
    config
    include/config.h
    )

'''


class TestCmakeParser(unittest.TestCase):
    def test_parser_complete_cmake_test(self):
        cmake = CMakeParser()
        cmake.parse(cmake_text)
        obtained = [include.name for include in cmake.includes]
        expected = ['src/Macros.cmake',
                    'src2/Macros2.cmake',
                    'src3/Macros3.cmake',
                    'include/CMakeLists.txt',
                    'config/Config']
        self.assertItemsEqual(expected, obtained)

    def test_parser_icnlude_test(self):
        cmake = CMakeParser()
        cmake.parse(cmake_includes_text)
        obtained = [include.name for include in cmake.includes]
        expected = ['src/Macros.cmake', 'src2/Macros2.cmake', 'Module/cmake/Macro.cmake']
        self.assertItemsEqual(expected, obtained)

    def test_parser_add_subdirectory_test(self):
        cmake = CMakeParser()
        cmake.parse(cmake_add_subdirectory_text)
        obtained = [include.name for include in cmake.includes]
        expected = ['cmake/CMakeLists.txt', 'src4/CMakeLists.txt']
        self.assertItemsEqual(expected, obtained)

    def test_parser_configure_file_test(self):
        cmake = CMakeParser()
        cmake.parse(cmake_configure_file_text)
        obtained = [include.name for include in cmake.includes]
        expected = ['src/Macros.cmake', 'config.h.in', 'config']
        self.assertItemsEqual(expected, obtained)


if __name__ == "__main__":
    unittest.main()
