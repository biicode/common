import unittest
from biicode.common.model.blob import Blob
from biicode.common.edition import changevalidator
from biicode.common.conf import BII_FILE_SIZE_LIMIT
from biicode.common.edition.changevalidator import BII_FILE_SIZE_LIMIT_STR
from biicode.common.output_stream import OutputStream


class ChangeValidatorTest(unittest.TestCase):

    def test_large_cell_reject(self):
        load = Blob("x" * (BII_FILE_SIZE_LIMIT))
        files = {"user/block/file": (None, load)}

        biiout = OutputStream()
        changevalidator.remove_large_cells(files, biiout)
        self.assertEquals(0, len(files))
        self.assertEquals("WARN: File user/block/file is bigger "
                          "than %s: discarded\n" % BII_FILE_SIZE_LIMIT_STR,
                          str(biiout))

    def test_size_reject_accept(self):
        load = Blob("x" * BII_FILE_SIZE_LIMIT)
        load2 = Blob("x" * (BII_FILE_SIZE_LIMIT - 1))
        files = {"user/block/filelarge":  (None, load),
                 "user/block/filesmall": (None, load2)}

        biiout = OutputStream()
        changevalidator.remove_large_cells(files, biiout)
        self.assertEquals(1, len(files))
        self.assertEquals("WARN: File user/block/filelarge is "
                          "bigger than %s: discarded\n" % BII_FILE_SIZE_LIMIT_STR,
                          str(biiout))
        self.assertIn("user/block/filesmall", files)
