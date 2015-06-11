import unittest

from biicode.common.test.bii_test_case import BiiTestCase
from biicode.common.edition.project_manager import ProjectManager
from biicode.common.find.finder_result import FinderResult
from biicode.common.find.policy import Policy
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.brl.brl_user import BRLUser
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.symbolic.reference import ReferencedDependencies
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.test.common.integration.tools.test_edition_api import TestEditionAPI
from biicode.common.model.brl.block_name import BlockName
from biicode.common.find.find_manager import update_hive_with_find_result
from biicode.common.output_stream import OutputStream


class FindRequestTest(BiiTestCase):

    def setUp(self):
        self.testuser = BRLUser('user')
        self.edition_api = TestEditionAPI()
        self.hive_manager = ProjectManager(self.edition_api, None, OutputStream())
        self.block_name = BlockName('dummy/myblock')

    def test_compute_request(self):
        files = {self.block_name + 'main.cpp': '#include "user2/block/sphere.h"'}
        self.hive_manager.process(None, files)

        find_request, unresolved = self.hive_manager.hive_holder.find_request(Policy.default())
        self.assertIn(CPPDeclaration('user2/block/sphere.h'), find_request.unresolved)
        self.assertEqual(unresolved, set())

    def test_no_unresolved_to_local(self):
        files = {self.block_name + 'main.cpp': '#include "dummy/myblock/sphere.h"'}
        self.hive_manager.process(None, files)

        find_request, unresolved = self.hive_manager.hive_holder.find_request(Policy.default())
        self.assertEqual(set(), find_request.unresolved)
        self.assertEqual(unresolved, {CPPDeclaration("dummy/myblock/sphere.h")})

    def test_apply_result(self):
        # TODO: this is actually a test of find result, move away
        files = {self.block_name + 'main.cpp': '#include "user2/block/sphere.h"'}
        self.hive_manager.process(None, files)

        find_result = FinderResult()
        version = BRLBlock('user2/user2/block/branch') + 3
        d = ReferencedDependencies()
        decl = CPPDeclaration('user2/block/sphere.h')
        d[version][decl].add(BlockCellName('user2/block/sphere.h'))
        find_result.resolved = d

        hive_holder = self.hive_manager.hive_holder
        update_hive_with_find_result(hive_holder, find_result)

        self.assertEqual(2, len(hive_holder.resources))
        self.assertEqual(BlockVersionTable([version]), hive_holder[self.block_name].requirements)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
