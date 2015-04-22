import unittest
from biicode.common.edition.checkin import obtain_types_blobs, CheckinManager
from biicode.common.model.bii_type import CPP
from biicode.common.model.blob import Blob
import os
from biicode.common.settings.settings import Settings
from mock import Mock
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.edition.hive_holder import HiveHolder
from biicode.common.edition.hive import Hive


class ChekinTest(unittest.TestCase):

    def obtain_types_blobs_test(self):
        files = {'afile1.c': 'Hello\r\n',
                 'bii/file2.c': 'Bye\n'}
        normalize = True
        result = obtain_types_blobs(files, normalize)
        self.assertEqual({'afile1.c': (CPP, Blob('Hello%s' % os.linesep, normalize=normalize)),
                          'bii/file2.c': (CPP, Blob('Bye%s' % os.linesep, normalize=normalize))},
                         result)

        # Now not normalize
        normalize = False
        result = obtain_types_blobs(files, normalize)
        self.assertEqual(result["afile1.c"][1].bytes, 'Hello\r\n')
        self.assertEqual(result["bii/file2.c"][1].bytes, 'Bye\n')

    def checkin_manager_test(self):
        '''
        Tests CheckinManager and normalizing.
        Instance a ChekinManager and checkin files, first normalizing and
        then without normalizing
        '''
        settings = Mock(Settings())
        settings.user = {"autocrlf": True}
        hive_holder = HiveHolder(Hive(), {}, {})
        biiout = Mock()
        manager = CheckinManager(hive_holder, settings, biiout)

        files = {BlockCellName('user/block/file1.c'): 'Hello\r\n',
                 BlockCellName('user/block2/file2.c'): 'Bye\n'}

        manager.checkin_files(files)

        file1_content = hive_holder.resources["user/block/file1.c"].content.load.bytes
        self.assertEqual(file1_content, 'Hello%s' % os.linesep)

        file2_content = hive_holder.resources["user/block2/file2.c"].content.load.bytes
        self.assertEqual(file2_content, 'Bye%s' % os.linesep)

        # Now not normalize
        settings.user = {"autocrlf": False}
        manager.checkin_files(files)

        file1_content = hive_holder.resources["user/block/file1.c"].content.load.bytes
        self.assertEqual(file1_content, 'Hello\r\n')

        file2_content = hive_holder.resources["user/block2/file2.c"].content.load.bytes
        self.assertEqual(file2_content, 'Bye\n')
