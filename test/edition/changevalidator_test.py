import unittest
from biicode.common.edition.hive import Hive
from biicode.common.model.blob import Blob
from biicode.common.exception import BiiException
from biicode.common.edition import changevalidator
from biicode.common.edition.processors.processor_changes import ProcessorChanges
from biicode.common.conf import BII_FILE_SIZE_LIMIT, BII_HIVE_NUMFILES_LIMIT
from biicode.common.edition.changevalidator import BII_FILE_SIZE_LIMIT_STR
from biicode.common.output_stream import OutputStream
from biicode.common.model.content import Content


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

    def test_hive_num_files_reject(self):
        with self.assertRaises(BiiException):
            hive = Hive()
            changes = ProcessorChanges()
            for i in xrange(BII_HIVE_NUMFILES_LIMIT + 1):
                name = "user/block/file%d" % i
                changes.upsert(name, Content(id_=name, load=Blob()))
            hive.update(changes)
            changevalidator.check_hive_num_cells(hive)
