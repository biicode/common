import unittest
from biicode.common.model.content import Content
from biicode.common.model.blob import Blob
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.brl.brl_user import BRLUser
from biicode.common.model.cells import SimpleCell
from biicode.common.model.resource import Resource, resource_diff_function
from biicode.common.diffmerge.differ import compute_diff
from biicode.common.diffmerge.compare import compare


class CompareLocalWithTrackingTest(unittest.TestCase):

    def setUp(self):
        testUser = BRLUser('compareUser')
        self.brl_block = BRLBlock('%s/%s/%s/master' % (testUser, testUser, 'modulea'))
        r1 = SimpleCell(self.brl_block.block_name + 'r1.h')
        content = Content(id_=None, load=Blob('hello'))
        self.r1 = r1
        self.c1 = content
        self.last_version_resources = {'r1.h': Resource(r1, content)}

    def test_modify_content(self):
        '''just modify the content of a file'''
        r1 = SimpleCell(self.brl_block.block_name + 'r1.h')
        content = Content(id_=None, load=Blob('bye'))

        edition_resources = {'r1.h': Resource(r1, content)}

        changes = compare(self.last_version_resources, edition_resources)

        self.assertEqual(0, len(changes.deleted))
        self.assertEqual(0, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(1, len(changes.modified))
        self.assertEqual(Resource(r1, content), changes.modified['r1.h'].new)

    def test_modify_content_diff(self):
        r1 = SimpleCell(self.brl_block.block_name + 'r1.h')
        content = Content(id_=None, load=Blob('bye'))
        edition_resources = {'r1.h': Resource(r1, content)}
        changes = compare(self.last_version_resources, edition_resources)

        diff = compute_diff(changes, resource_diff_function)

        self.assertEqual(0, len(diff.deleted))
        self.assertEqual(0, len(diff.created))
        self.assertEqual(0, len(diff.renames))
        self.assertEqual(1, len(diff.modified))
        self.assertEqual('--- base\n\n+++ other\n\n@@ -1 +1 @@\n\n-hello\n+bye',
                         diff.modified['r1.h'].content)
        #print '--- base\n\n+++ other\n\n@@ -1 +1 @@\n\n-hello\n+bye'
        self.assertEqual(Resource(None, '--- base\n\n+++ other\n\n@@ -1 +1 @@\n\n-hello\n+bye'),
                         diff.modified['r1.h'])

    def test_create_resource(self):

        r1 = SimpleCell(self.brl_block.block_name + 'r1.h')
        content = Content(id_=None, load=Blob('hello'))

        r2 = SimpleCell(self.brl_block.block_name + 'r2.h')
        content2 = Content(id_=None, load=Blob('bye'))

        edition_resources = {'r1.h': Resource(r1, content), 'r2.h': Resource(r2, content2)}
        changes = compare(self.last_version_resources, edition_resources)

        self.assertEqual(0, len(changes.deleted))
        self.assertEqual(1, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(0, len(changes.modified))
        self.assertEqual(Resource(r2, content2), changes.created['r2.h'])

    def test_delete_resource(self):

        edition_resources = {}
        changes = compare(self.last_version_resources, edition_resources)

        self.assertEqual(1, len(changes.deleted))
        self.assertEqual(0, len(changes.created))
        self.assertEqual(0, len(changes.renames))
        self.assertEqual(0, len(changes.modified))
        self.assertEqual((self.r1, self.c1), changes.deleted['r1.h'])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
