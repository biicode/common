import unittest
from copy import copy
from mock import Mock
from biicode.common.model.blob import Blob
from biicode.common.output_stream import OutputStream
from biicode.common.diffmerge.update import BlobsMerger


class ResourcesMergeTest(unittest.TestCase):

    def setUp(self):

        self.common = self._make_resources(
                    {
                     'user/block1/file1.h': "file1content",
                     'user/block1/file2.h': "file2content",
                     'user/block1/file3.h': "file3content",
                    }
                )

    def test_no_compare(self):
        base = copy(self.common)
        other = self._make_resources(
                    {
                     'user/block1/file1.h': "file1content@modified",
                    }
                )

        merger = BlobsMerger("user/block1#1", "user/block1#2", OutputStream())
        merger.merge_elements = Mock(side_effect=Exception("No item must be compared!"))
        ret = merger.merge(base, other, self.common)
        self.assertEquals(ret['user/block1/file1.h'].load, "file1content@modified")

    def test_with_compare(self):
        base = self._make_resources({'user/block1/file1.h': "@modified1"})
        other = self._make_resources({'user/block1/file1.h': "@modified2"})
        output = OutputStream()
        merger = BlobsMerger("user/block1#1", "user/block1#2", output)
        ret = merger.merge(base, other, self.common)
        self.assertEquals(ret['user/block1/file1.h'].bytes,
'''<<<<<<<<<<<<<<<<<<<<<<<<< user/block1#1
@modified1
=========================
@modified2
>>>>>>>>>>>>>>>>>>>>>>>>> user/block1#2
''')
        self.assertIn("CONFLICT", str(output))

    def test_with_binary_blobs(self):
        base = self._make_resources(
                    {
                     'user/block1/file1.h': "@modified1",
                    }, is_binary=True
                )
        other = self._make_resources(
                    {
                     'user/block1/file1.h': "@modified2",
                    }
                )

        output = OutputStream()
        merger = BlobsMerger("user/block1#1", "user/block1#2", output)
        merger.merge(base, other, self.common)
        self.assertIn("CONFLICT", str(output))
        self.assertIn("WARN: Can't merge binary contents, your file is keeped", str(output))
        self.assertIn('user/block1/file1.h: CONFLICT (modified/modified): Changed in '
                      'user/block1#1 and changed in user/block1#2', str(output))

    def _make_resources(self, dict_cells, is_binary=False):
        return {path: Blob(blob=content, is_binary=is_binary)
                for path, content in dict_cells.iteritems()}
