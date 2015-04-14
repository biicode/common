import unittest
from biicode.common.edition.checkin import obtain_types_blobs
from biicode.common.model.bii_type import CPP
from biicode.common.model.blob import Blob


class ChekinTest(unittest.TestCase):

    def obtain_types_blobs_test(self):
        files = {'afile1.c': 'Hello',
                 'bii/file2.c': 'Bye'}
        result = obtain_types_blobs(files)
        self.assertEqual({'afile1.c': (CPP, Blob('Hello')),
                          'bii/file2.c': (CPP, Blob('Bye'))},
                         result)

