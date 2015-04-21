import unittest
from os import linesep
from biicode.common.model.blob import Blob
from biicode.common.test.conf import BII_TEST_FOLDER
import tempfile
import os
from biicode.common.utils.file_utils import save
import time
from nose_parameterized import parameterized
from bson.binary import Binary

unixsep = "\n"
winsep = "\r\n"

unix_text = "FirstLine %sSecondLine%s\ttabs \t and \t tabs%s" % (unixsep, unixsep, unixsep)
win_text = "FirstLine %sSecondLine%s\ttabs \t and \t tabs%s" % (winsep, winsep, winsep)
sys_text = "FirstLine %sSecondLine%s\ttabs \t and \t tabs%s" % (linesep, linesep, linesep)
compressed = Binary('x\x9cs\xcb,*.\xf1\xc9\xccKU\xe0\nNM\xce\xcfK\x01\xb1\xb98K'
                    '\x12\x93\x8a\x158\x15\x12\xf3R\x80$\x88\xc3\x05\x00 R\x0c\xd5')


class BlobUnitTest(unittest.TestCase):

    @parameterized.expand([(unix_text,), (win_text,), (sys_text,)])
    def test_normalize(self, text):
        blob = Blob(text)
        self.assertEqual(blob.bytes, unix_text)
        self.assertEqual(blob.sha, "ac517966fd59bb4bd3731273b8fbc96414866eda")
        self.assertEqual(blob, Blob(win_text))
        self.assertNotEqual(blob, Blob("Hello"))
        self.assertEqual(blob.load, sys_text)

        s = blob.serialize()
        self.assertEqual(s['c'], compressed)

        blob3 = Blob.deserialize(s)
        self.assertEqual(blob, blob3)
        self.assertEqual(blob3.bytes, unix_text)

    def test_empty_file_size(self):
        cl = Blob('')
        #Normalize text append \n if doesn't exist.
        self.assertEqual(0, cl.size)

    def test_plain_text_size(self):
        cl = Blob(win_text)
        self.assertEqual(41, cl.size)

    def test_binary_size(self):
        cl = Blob(compressed, is_binary=True)
        self.assertEqual(43, cl.size)

    def test_similarity(self):
        cl = Blob(win_text)
        c2 = Blob(unix_text)
        self.assertEquals(cl.similarity(c2), 1.0)

    def test_similarity_binary(self):
        cl = Blob(compressed, True)
        cl2 = Blob(compressed, True)
        self.assertEquals(cl.similarity(cl2), 1.0)

    def test_similarity_binary_distinct(self):
        cl = Blob("Hello", True)
        cl2 = Blob("Hello1", True)
        self.assertEquals(cl.similarity(cl2), 0.0)
