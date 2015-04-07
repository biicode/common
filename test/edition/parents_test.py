import unittest
from biicode.common.exception import ConfigurationFileError
from biicode.common.edition.parsing.conf.parent import parent_loads


class ParentsTest(unittest.TestCase):

    def test_invalid(self):
        with self.assertRaisesRegexp(ConfigurationFileError,
                                     "Impossible to have two main parents"):
            parent_loads('* testuser0/block2: 0\ntestuser3/block3: 0', 0)
