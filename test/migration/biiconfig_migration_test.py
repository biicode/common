import unittest
from biicode.common.output_stream import OutputStream
from biicode.common.migrations.biiconfig_migration import migrate_bii_config


all_files = {'user/block/bii/parents.bii': 'john/smith: 3',
             'user/block/file.cpp': "//bii://mydata.txt",
             'user/block/projetc.sln': "//bii://mydata2.txt",
             'user/block/file_proj.vcproj': "//bii://mydata3.txt"}


class BiiconfigMigrationTest(unittest.TestCase):

    def test_migrate_with_several_files(self):
        biiout = OutputStream()
        deleted = migrate_bii_config(all_files, biiout)
        self.assertEqual(deleted, ['user/block/bii/parents.bii'])
        self.assertIn('file.cpp + mydata.txt', all_files['user/block/biicode.conf'])
        self.assertIn('john/smith: 3', all_files['user/block/biicode.conf'])
        self.assertIn('file.cpp + mydata.txt', all_files['user/block/biicode.conf'])
        self.assertNotIn('mydata2.txt', all_files['user/block/biicode.conf'])
        self.assertNotIn('mydata3.txt', all_files['user/block/biicode.conf'])
