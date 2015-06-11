import unittest
from biicode.common.edition.project_holder import ProjectHolder
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.resource import Resource
from biicode.common.model.cells import SimpleCell
from biicode.common.model.content import Content
from biicode.common.model.blob import Blob
from biicode.common.edition.block_holder import BlockHolder, BIICODE_FILE

a1 = BlockVersion.loads('user0/blocka: 1')
an = BlockVersion.loads('user0/blocka')
b2 = BlockVersion.loads('user0/blockb(branch): 2')
bn = BlockVersion.loads('user0/blockb(branch)')
cn = BlockVersion.loads('user0/blockc: -1')


class ProjectHolderTest(unittest.TestCase):

    def base_version_test(self):
        hive_holder = ProjectHolder({}, {})
        parents_resource = Resource(SimpleCell(a1.block_name + BIICODE_FILE),
                                    Content(id_=None, load=Blob('[parent]\n ' + str(a1))))
        hive_holder.add_holder(BlockHolder(a1.block_name, {parents_resource}))
        parents_resource = Resource(SimpleCell(b2.block_name + BIICODE_FILE),
                                    Content(id_=None, load=Blob('[parent]\n * ' + str(b2))))
        hive_holder.add_holder(BlockHolder(b2.block_name, {parents_resource}))
        hive_holder.add_holder(BlockHolder(cn.block_name, {}))
        result_table = BlockVersionTable([b.parent for b in hive_holder.block_holders])
        self.assertEqual(result_table, BlockVersionTable([a1, b2, cn]))
