import unittest
from mock import Mock
from biicode.common.model.content import Content
from biicode.common.model.content import ContentDeserializer
from biicode.common.model.content import content_diff
from biicode.common.exception import BiiSerializationException
from biicode.common.model.id import ID


class ContentTest(unittest.TestCase):

    def test_deserialize_exception(self):
        self.assertRaises(BiiSerializationException,
                          ContentDeserializer(ID((0, 0, 0))).deserialize,
                          "wrong object")
        self.assertIsNone(ContentDeserializer(ID).deserialize(None))

    def test_content_diff(self):
        content_load1 = Mock()
        content_load2 = Mock()
        content_load1.is_binary = Mock(return_value=True)
        self.assertEquals(content_diff(content_load1, content_load2),
                          "Unable to diff binary contents of base")
        content_load1.is_binary = Mock(return_value=False)
        content_load2.is_binary = Mock(return_value=True)
        self.assertEquals(content_diff(content_load1, content_load2),
                          "Unable to diff binary contents of base")

    def test_content_similarity(self):
        content = Content(ID((0, 0, 0)), load=None)
        self.assertEquals(content.similarity(content), 1)
