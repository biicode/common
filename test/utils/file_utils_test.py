import unittest
import tempfile
import os
from biicode.common.utils import file_utils as fileUtils
from uuid import uuid4
from biicode.common.test.conf import BII_TEST_FOLDER


class MyClass:
    def __init__(self):
        self.name = str(uuid4())


class TestFileUtils(unittest.TestCase):
    _suites = ['common']

    def setUp(self):
        self.hiveFolder = tempfile.mkdtemp(suffix='fileUtils', dir=BII_TEST_FOLDER)
    def testGetFilesRecursive(self):

        os.mkdir(os.path.join(self.hiveFolder, '.bii'))
        os.mkdir(os.path.join(self.hiveFolder, 'other'))
        settingsPath = os.path.join(self.hiveFolder, '.bii', 'settings.json')
        dummy1Path = os.path.join(self.hiveFolder, 'myFile1.h')
        dummy2Path = os.path.join(self.hiveFolder, 'other', 'myFile2.c')
        dummy3Path = os.path.join(self.hiveFolder, 'other', 'myFile2.h')

        files = [settingsPath, dummy1Path, dummy2Path, dummy3Path]
        for p in files:
            f = open(p, 'w+')
            f.close()
        vfiles = fileUtils.get_files_recursive(self.hiveFolder,"*.h")
        for i in ['myFile1.h', os.path.join('other', 'myFile2.h')]:
            self.assertIn(i, vfiles)
        self.assertFalse(os.path.join('other', 'myFile2.c') in vfiles)

    def testRecursiveVisibleFiles(self):
        os.mkdir(os.path.join(self.hiveFolder, '.bii'))
        os.mkdir(os.path.join(self.hiveFolder, 'other'))
        settingsPath = os.path.join(self.hiveFolder, '.bii', 'settings.json')
        dummy1Path = os.path.join(self.hiveFolder, 'myFile1')
        dummy2Path = os.path.join(self.hiveFolder, 'other', 'myFile2')
        invisible = os.path.join(self.hiveFolder, '.invisible')

        files = [settingsPath, dummy1Path, dummy2Path, invisible]
        for p in files:
            f = open(p, 'w+')
            f.close()
        vfiles = fileUtils.get_visible_files_recursive(self.hiveFolder)
        for i in [settingsPath, dummy1Path, dummy2Path]:
            self.assertIn(i, vfiles)
        self.assertFalse(invisible in vfiles)

    def test_file_normalize_line_sep(self):
        '''testing that open text file with rU really normalizes text'''
        folder = tempfile.mkdtemp(suffix='biicode', dir=BII_TEST_FOLDER)
        binary_content = 'Hola\nQue tal\r\nYo bien\rY tu qe tal?\r\r\nAgur'
        path = os.path.join(folder, 'test.txt')
        with open(path, 'wb') as handle:
            handle.write(binary_content)
        with open(path, 'rU') as handle:
            text_contents = handle.read()
            self.assertEqual(-1, text_contents.find(r'\r'))
