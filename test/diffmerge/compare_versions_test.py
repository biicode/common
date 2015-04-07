from biicode.common.model.bii_type import CPP, UNKNOWN
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.brl.brl_user import BRLUser
from biicode.common.model.content import Content
from biicode.common.model.blob import Blob
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.cells import SimpleCell
import unittest
from biicode.common.model.brl.cell_name import CellName
from biicode.common.diffmerge.differ import compute_diff
from biicode.common.model.resource import resource_diff_function, Resource
from biicode.common.diffmerge.compare import compare_remote_versions
from biicode.common.model.renames import Renames
from biicode.common.edition.block_holder import BlockHolder


def get_block_holder(block_name, resources_defs):
    resources = {}
    for cell_name, (typ, text) in resources_defs.iteritems():
        if typ is None:
            typ = UNKNOWN
        cell = SimpleCell(block_name + cell_name, typ)
        resources[cell_name] = Resource(cell, Content(block_name + cell_name, load=Blob(text)))
    return BlockHolder(block_name, resources)


class FakeService(object):
    def __init__(self, block):
        self.block = block

    def get_renames(self, brl_block, t1, t2):
        ret = Renames()
        if t2 == 6:
            ret[CellName("r1.h")] = CellName("r3.h")
        elif t2 == 7:
            ret[CellName("r3.h")] = CellName("r4.h")

        return ret

    def get_block_holder(self, block_version):
        assert self.block == block_version.block
        holders = [{'r1.h': (None, 'hello')},  # 0
                 {'r1.h': (None, 'hello2')},  # 1 Content change
                 {'r1.h': (CPP, 'hello2')},  # 2 cell change
                 {'r1.h': (None, 'hello3')},  # 3 Cell and content change
                 {'r1.h': (None, 'hello3'),
                  'r2.h': (None, 'bye')},  # 4 Cell and content add
                 {'r1.h': (None, 'hello3')},  # 5 Remove
                 {'r3.h': (None, 'hello3')},  # 6 Rename without change
                 {'r4.h': (None, 'hello4')}  # 7 Rename with changes
                 ]
        holder = get_block_holder(block_version.block_name, holders[block_version.time])
        return holder


class CompareVersionsTest(unittest.TestCase):
    '''This test checks comparisons between published
    versions of the same block, both "changes" and "diff"'''

    def setUp(self):
        test_user = BRLUser('compareUser')
        self.block = BRLBlock('%s/%s/%s/master' % (test_user, test_user, 'blocka'))
        self.service = FakeService(self.block)

    def test_content_modify(self):
        '''check between time 0 and 1, just a content edit'''
        version0 = BlockVersion(self.block, 0)
        version1 = BlockVersion(self.block, 1)
        changes = compare_remote_versions(self.service, version0, version1)
        self.assertEqual(0, len(changes.deleted))
        self.assertEqual(0, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(1, len(changes.modified))
        diff = compute_diff(changes, resource_diff_function)
        self.assertEqual((None, '--- base\n\n+++ other\n\n@@ -1 +1 @@\n\n'
                                '-hello\n+hello2'),
                         diff.modified['r1.h'])

    def test_cell_modify(self):
        '''check between time 1 and 2, a BiiType change'''
        version1 = BlockVersion(self.block, 1)
        version2 = BlockVersion(self.block, 2)
        changes = compare_remote_versions(self.service, version1, version2)

        self.assertEqual(0, len(changes.deleted))
        self.assertEqual(0, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(1, len(changes.modified))
        self.assertEqual(UNKNOWN,
                         changes.modified['r1.h'].old.cell.type)
        self.assertEqual(CPP,
                         changes.modified['r1.h'].new.cell.type)
        #diff = compute_diff(changes, resource_diff_function)
        #TODO: Implement and check diff of cell

    def test_cell_content_modify(self):
        '''between time 0 and 2 there is content and biitype change'''
        version0 = BlockVersion(self.block, 0)
        version2 = BlockVersion(self.block, 2)
        changes = compare_remote_versions(self.service, version0, version2)

        self.assertEqual(0, len(changes.deleted))
        self.assertEqual(0, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(1, len(changes.modified))
        self.assertEqual(UNKNOWN,
                         changes.modified['r1.h'].old.cell.type)
        self.assertEqual(CPP,
                         changes.modified['r1.h'].new.cell.type)
        diff = compute_diff(changes, resource_diff_function)
        self.assertEqual('--- base\n\n+++ other\n\n@@ -1 +1 @@\n\n'
                         '-hello\n+hello2',
                         diff.modified['r1.h'].content)
        #TODO: Implement and check diff of cell

    def test_cell_content_modify_single_step(self):
        ''' 2=> 3 content modify and biitype change in single step'''
        version2 = BlockVersion(self.block, 2)
        version3 = BlockVersion(self.block, 3)
        changes = compare_remote_versions(self.service, version2, version3)

        self.assertEqual(0, len(changes.deleted))
        self.assertEqual(0, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(1, len(changes.modified))
        self.assertEqual(CPP,
                         changes.modified['r1.h'].old.cell.type)
        self.assertEqual(UNKNOWN,
                         changes.modified['r1.h'].new.cell.type)
        diff = compute_diff(changes, resource_diff_function)
        self.assertEqual('--- base\n\n+++ other\n\n@@ -1 +1 @@\n\n'
                        '-hello2\n+hello3',
                         diff.modified['r1.h'].content)
        #TODO: Implement and check diff of cell
        self.assertIsNotNone(diff.modified['r1.h'].cell)

    def test_resource_created(self):
        ''' 3 => 4 cell creation'''
        version3 = BlockVersion(self.block, 3)
        version4 = BlockVersion(self.block, 4)
        changes = compare_remote_versions(self.service, version3, version4)

        self.assertEqual(0, len(changes.deleted))
        self.assertEqual(1, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(0, len(changes.modified))
        diff = compute_diff(changes, resource_diff_function)
        self.assertEqual('--- base\n\n+++ other\n\n@@ -0,0 +1 @@\n\n+bye',
                         diff.created['r2.h'].content)
        #TODO: Implement and check diff of cell
        self.assertIsNotNone(diff.created['r2.h'].cell)

    def test_delete(self):
        '''4 => 5 r2.h is deleted'''
        version4 = BlockVersion(self.block, 4)
        version5 = BlockVersion(self.block, 5)
        changes = compare_remote_versions(self.service, version4, version5)

        self.assertEqual(1, len(changes.deleted))
        self.assertEqual(0, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(0, len(changes.modified))
        diff = compute_diff(changes, resource_diff_function)
        self.assertEqual('--- base\n\n+++ other\n\n@@ -1 +0,0 @@\n\n-bye',
                         diff.deleted['r2.h'].content)
        self.assertIsNotNone(diff.deleted['r2.h'].cell)

    def test_rename(self):
        version5 = BlockVersion(self.block, 5)
        version6 = BlockVersion(self.block, 6)
        changes = compare_remote_versions(self.service, version5, version6)

        self.assertEqual(1, len(changes.deleted))
        self.assertEqual(1, len(changes.created))
        self.assertEqual(1, len(changes.renames))
        self.assertEqual(0, len(changes.modified))
        self.assertEqual('r3.h', changes.renames['r1.h'])
        diff = compute_diff(changes, resource_diff_function)
        self.assertEqual(0, len(diff.deleted))
        self.assertEqual(0, len(diff.created))
        self.assertEqual('', diff.modified['r1.h'].content)
        self.assertIsNotNone(diff.modified['r1.h'].cell)
        self.assertEqual('r3.h', diff.renames['r1.h'])

    def test_rename_changes(self):
        version6 = BlockVersion(self.block, 6)
        version7 = BlockVersion(self.block, 7)
        changes = compare_remote_versions(self.service, version6, version7)

        self.assertEqual(1, len(changes.deleted))
        self.assertEqual(1, len(changes.created))
        self.assertEqual(1, len(changes.renames))
        self.assertEqual(0, len(changes.modified))
        self.assertEqual('r4.h', changes.renames['r3.h'])
        diff = compute_diff(changes, resource_diff_function)
        self.assertEqual(0, len(diff.deleted))
        self.assertEqual(0, len(diff.created))
        self.assertEqual('--- base\n\n+++ other\n\n@@ -1 +1 @@\n\n'
                         '-hello3\n+hello4',
                         diff.modified['r3.h'].content)
        self.assertIsNotNone(diff.modified['r3.h'].cell)
        self.assertEqual('r4.h', diff.renames['r3.h'])

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
