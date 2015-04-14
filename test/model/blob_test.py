import unittest
from os import linesep
from biicode.common.model.blob import Blob, normalize_text
from biicode.common.model.blob import compress
from biicode.common.model.blob import uncompress
from biicode.common.model.blob import systemize_text
from biicode.common.exception import BiiException
from mock import Mock
import zlib
from biicode.common.test.conf import BII_TEST_FOLDER
import tempfile
import os
from biicode.common.utils.file_utils import save
import time


class BlobUnitTest(unittest.TestCase):

    syssep = linesep
    unixsep = "\n"
    winsep = "\r\n"

    unix_text = "FirstLine %sSecondLine%s\ttabs \t and \t tabs%s" % (unixsep, unixsep, unixsep)
    win_text = "FirstLine %sSecondLine%s\ttabs \t and \t tabs%s" % (winsep, winsep, winsep)
    sys_text = "FirstLine %sSecondLine%s\ttabs \t and \t tabs%s" % (syssep, syssep, syssep)

    nor_text = unix_text

    compressed = ('x\x9cs\xcb,*.\xf1\xc9\xccKU\xe0\nNM\xce\xcfK\x01\xb1\xb98K'
                  '\x12\x93\x8a\x158\x15\x12\xf3R\x80$\x88\xc3\x05\x00 R\x0c\xd5')

    def testNormalizedTextNotModified(self):
        cl = Blob()
        cl.normalizedText = self.nor_text
        self.assertEqual(self.nor_text, cl.normalizedText)

    def test_empty_file_size(self):
        cl = Blob('')
        #Normalize text append \n if doesn't exist.
        self.assertEqual(0, cl.size)

    def test_plain_text_size(self):
        cl = Blob(self.nor_text)
        self.assertEqual(41, cl.size)

    def test_binary_size(self):
        cl = Blob(blob=self.compressed, is_binary=True)
        self.assertEqual(43, cl.size)

    def testSysToNormalized(self):
        cl = Blob()
        cl.text = self.sys_text
        self.assertEqual(self.nor_text, cl.text)

        cl.text = self.win_text
        self.assertEqual(self.nor_text, cl.text)

    def testSysTextNotModified(self):
        cl = Blob()
        cl.text = self.sys_text
        self.assertEqual(BlobUnitTest.sys_text, cl.load)

    def testEncodeAndDecode(self):
        cl = Blob()
        cl.text = self.nor_text
        self.binary = cl.binary
        self.assertEqual(self.nor_text, cl.text)

    def testCompress(self):
        cl = Blob()
        cl.text = self.nor_text
        self.compressedBin = cl._compressed()
        self.assertEqual(self.nor_text, cl.text)

    def testEqualsSameSetter(self):
        cl = Blob()
        c2 = Blob()
        cl.text = self.sys_text
        c2.text = self.nor_text
        self.assertEqual(cl, c2)

        cl.normalizedText = self.nor_text
        c2.normalizedText = self.nor_text
        self.assertEqual(cl, c2)

        cl.compressedBin = self.compressed
        c2.compressedBin = self.compressed
        self.assertEqual(cl, c2)

    def testSysSetter(self):
        cl = Blob()
        c2 = Blob()
        cl.text = self.sys_text
        c2.text = self.nor_text
        self.assertEqual(cl, c2)

        c2.compressedBin = self.compressed
        self.assertEqual(cl, c2)

    def testNormSetter(self):
        cl = Blob()
        c2 = Blob()
        cl.text = self.nor_text
        c2.text = self.sys_text
        self.assertEqual(cl, c2)

        c2.compressedBin = self.compressed
        self.assertEqual(cl, c2)

    def test_similarity(self):
        cl = Blob()
        c2 = Blob()
        cl.text = self.nor_text
        c2.text = self.nor_text
        self.assertEquals(cl.similarity(c2), 1.0)

    def test_similarity_binary(self):
        cl = Blob(self.compressed, True)
        cl2 = Blob(self.compressed, True)
        self.assertEquals(cl.similarity(cl2), 1.0)

    def test_similarity_binary_distinct(self):
        cl = Blob(self.nor_text, True)
        cl2 = Blob(self.compressed, True)
        self.assertEquals(cl.similarity(cl2), 0.0)

    def test_eq(self):
        cl = Blob(self.nor_text, True)
        cl2 = Blob(self.compressed, True)
        self.assertEquals(cl, cl)
        self.assertNotEquals(cl, 1)
        self.assertNotEquals(cl, cl2)

    def test_compress(self):
        old_zlib_compress = zlib.compress
        zlib.compress = Mock(side_effect=IOError)
        self.assertRaises(BiiException, compress, "test")
        zlib.compress = old_zlib_compress

    def test_uncompress(self):
        old_zlib_decompress = zlib.decompress
        zlib.decompress = Mock(side_effect=IOError)
        self.assertRaises(BiiException, uncompress, "test")
        zlib.decompress = old_zlib_decompress

    def test_systemize(self):
        self.assertEquals(systemize_text(self.nor_text), self.sys_text)

    def test_speed_normalize(self):
        """ this test is only a helper to check performance of normalizing,
        actually the check is very coarse
        """
        folder = tempfile.mkdtemp(suffix='biicode', dir=BII_TEST_FOLDER)
        code = '\r\n'.join(['Hello how are you?' for _ in xrange(4000)])
        path = os.path.join(folder, 'test.cpp')
        save(path, code)
        start_time = time.time()
        count = 30
        for _ in xrange(count):
            with open(path, 'rU') as handle:
                content = handle.read()
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 0.2)
        #print elapsed

        start_time = time.time()
        for _ in xrange(count):
            with open(path, 'rb') as handle:
                content = handle.read()
                content = normalize_text(content)
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 0.2)
        #print elapsed
