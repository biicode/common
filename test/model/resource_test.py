import unittest
from biicode.common.edition.parsing.python.py_parser import PythonParser
from biicode.common.model.cells import SimpleCell, VirtualCell
from biicode.common.model.content import Content
from biicode.common.model.resource import Resource
from biicode.common.model.bii_type import PYTHON
from mock import patch
from biicode.common.model.blob import Blob
from biicode.common.output_stream import OutputStream


class ResourceTest(unittest.TestCase):

    @patch.object(PythonParser, 'parse')
    def python_parse_failure_test(self, parser):
        """ Weird bug miguel found.
        Python parser failure was causing 'You're trying to parse a virtual file' message to appear
        """
        response = OutputStream()
        parser.side_effect = Exception
        cell = SimpleCell('usr/block/sort_controllers.py', biitype=PYTHON)
        content = Content(id_=1, load=Blob('print "hello"'), parser=None, is_parsed=False)
        resource = Resource(cell, content)
        self.assertFalse(resource.parse(response))
        self.assertIn('Error parsing usr/block/sort_controllers.py file', str(response))

    def parse_virtual_test(self):
        response = OutputStream()
        cell = VirtualCell('usr/block/sort_controllers.py')
        resource = Resource(cell, None)
        self.assertFalse(resource.parse(response))
        self.assertIn('You\'re trying to parse a virtual file: usr/block/sort_controllers.py',
                      str(response))
