from biicode.common.test.bii_test_case import BiiTestCase
from biicode.common.edition.bii_config import BiiConfig
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.edition.parsing.conf.main_conf_file_parser import EntryPointConfiguration

parent1 = """
[parent]
    # The parent version of this block
     user/block: 0
"""

parent2 = """
[parent]
    user/block: 0 #comment
"""

parent3 = """
[parent]
#user/block: 0 #comment
"""

parent4 = """
[parent]
    user/block(track)
"""

general = """
# Biicode config file

[requirements]
    # Put here your required blocks
     user/depblock1: 3
     user2/depblock2(track):3@tag

[parent]
    # The parent version of this block
     user/block: 0

[paths]
    # Local block directories to look for headers (within block)
    /
    include

[includes]
    # Mapping of include patterns to external blocks
     hello*.h: user3/depblock  # includes will be processed as user3/depblock/hello*.h

[dependencies]
    # Manual adjust file dependencies
     hello.h + hello_imp.cpp
     *.h + *.cpp

[mains]
    # Manual adjust of files that define an executable
     !main.cpp  # Do not build executable from this file
     main2.cpp # Build it (it doesnt have a main() function, but maybe it includes it)

[tests]
    # Convert your executables into a test
    test.cpp
    # test4.cpp
    test1.cpp

[cpp-std]
    c++11 PRIVATE
    # c++14
    c++14

[hooks]
post: bii/myhook.py

[data]

#FALSE


"""


class BiiConfigTest(BiiTestCase):

    def empty_test(self):
        config = BiiConfig("")
        self.assertEqual(config.parent, None)
        self.assertEqual(config.requirements, BlockVersionTable())
        self.assertEqual(config.mains, [])
        self.assertEqual(config.dependencies, [])
        self.assertEqual(None, config.dumps())

    def parent_test(self):
        block_name = BlockName("user/block")
        version = BlockVersion(block_name.default_block(), 0)
        for text in (parent1, parent2):
            config = BiiConfig(text)
            self.assertEqual(config.parent, version)
            self.assertEqual(None, config.dumps())

        config = BiiConfig(parent3)
        self.assertEqual(config.parent, None)
        self.assertEqual(None, config.dumps())

        version = BlockVersion.loads("user/block(track): -1")
        config = BiiConfig(parent4)
        self.assertEqual(config.parent, version)
        self.assertEqual(None, config.dumps())

    def general_load_test(self):
        block_name = BlockName("user/block")
        version = BlockVersion(block_name.default_block(), 0)
        config = BiiConfig(general)
        self.assertEqual(config.parent, version)
        v1 = BlockVersion.loads("user2/depblock2(track): 3 @tag")
        v2 = BlockVersion.loads("user/depblock1(master): 3")
        self.assertEqual(config.requirements, BlockVersionTable([v1, v2]))
        self.assert_bii_equal(config.mains, [EntryPointConfiguration("main.cpp", False),
                                             EntryPointConfiguration("main2.cpp", True),
                                             ])
        self.assert_bii_equal(config.tests, ["test.cpp", "test1.cpp"])
        self.assertEqual(config.paths, ["/", "include"])
        self.assertEqual(config.cpp_std, ["c++11 PRIVATE", "c++14"])

    def requirements_update_test(self):
        block_name = BlockName("user/block")
        text = "[requirements]\n # My comment\n"
        config = BiiConfig(text)
        self.assertEqual(config.dumps(), None)

        version = BlockVersion(block_name.default_block(), 0)
        config.requirements = BlockVersionTable([version])
        dumped = config.dumps()
        self.assertEqual(dumped, "[requirements]\n\t user/block: 0\n\n")
        # Dump again, no changes
        self.assertEqual(config.dumps(), None)
        config2 = BiiConfig(dumped)
        self.assertEqual(config2.requirements, config.requirements)

        block_name2 = BlockName("auser2/block2")
        version2 = BlockVersion(block_name2.default_block(), 2)
        config.requirements = BlockVersionTable([version, version2])
        dumped = config.dumps()
        self.assertEqual(dumped, "[requirements]\n"
                                 "\t auser2/block2: 2\n\t user/block: 0\n\n")
        # Dump again, no changes
        self.assertEqual(config.dumps(), None)
        config3 = BiiConfig(dumped)
        self.assertEqual(config3.requirements, config.requirements)

    def parent_update_test(self):
        block_name = BlockName("user/block")
        text = "[parent]\n # My comment\n"
        config = BiiConfig(text)
        self.assertEqual(config.dumps(), None)

        version = BlockVersion(block_name.default_block(), 0)
        config.parent = version
        dumped = config.dumps()
        self.assertEqual(dumped, "[parent]\n\tuser/block: 0\n")
        # Dump again, no changes
        self.assertEqual(config.dumps(), None)
        config2 = BiiConfig(dumped)
        self.assertEqual(config2.parent, config.parent)

        version2 = BlockVersion.loads("user/block(track): 2")
        config.parent = version2
        dumped = config.dumps()
        self.assertEqual(dumped, "[parent]\n\tuser/block(track): 2\n")
        # Dump again, no changes
        self.assertEqual(config.dumps(), None)
        config3 = BiiConfig(dumped)
        self.assertEqual(config3.parent, config.parent)
