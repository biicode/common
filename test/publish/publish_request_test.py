from biicode.common.publish.publish_request import PublishRequest
from biicode.common.model.cells import SimpleCell
from biicode.common.diffmerge.changes import Changes, Modification
from biicode.common.model.content import Content
from biicode.common.model.resource import Resource
from biicode.common.model.renames import Renames
from biicode.common.model.bii_type import CPP
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.blob import Blob
from biicode.common.model.id import ID
from biicode.common.test.bii_test_case import BiiTestCase


class PublishRequestTest(BiiTestCase):

    @staticmethod
    def _changes():
        changes = Changes()
        changes.deleted['deleted'] = Resource(None, 'old_content')
        changes.deleted['renamed'] = Resource(SimpleCell('usr/block/renamed'),
                                              Content(ID((1234,)), load=Blob('old_content2')))
        changes.created['created'] = Resource(SimpleCell('usr/block/created'),
                                              Content(id_=None, load=Blob('created')))
        changes.created['renamed2'] = Resource(SimpleCell('usr/block/renamed2'),
                                               Content(id_=None, load=Blob('old_content2')))
        changes.modified['modified_cont'] = Modification(
                                                    Resource(SimpleCell('usr/block/modified_cont'),
                                                             Content(id_=None, load=Blob('mod_content'))),
                                                    Resource(SimpleCell('usr/block/modified_cont'),
                                                             Content(id_=None, load=Blob('mod_content2'))))
        changes.modified['modified_cell'] = Modification(
                                                    Resource(SimpleCell('usr/block/modified_cell'),
                                                             Content(id_=None, load=Blob('mod_cell'))),
                                                    Resource(SimpleCell('usr/block/modified_cell',
                                                                        CPP),
                                                             Content(id_=None, load=Blob('mod_cell'))))
        changes.modified['modified_both'] = Modification(
                                                    Resource(SimpleCell('usr/block/modified_both'),
                                                             Content(id_=None, load='mod_both')),
                                                    Resource(SimpleCell('usr/block/modified_both',
                                                                        CPP),
                                                             Content(id_=None, load=Blob('mod_both2'))))
        changes.renames = Renames({'renamed': 'renamed2'})
        return changes

    def test_empty_changes(self):
        p = PublishRequest()
        self.assertFalse(bool(p))

    def test_set_changes(self):
        p = PublishRequest()
        changes = self._changes()
        p.changes = changes
        self.assertTrue(bool(p))
        self.assertItemsEqual(['deleted', 'renamed'], p.deleted)
        self.assertEqual(changes.renames, p.renames)
        self.assertEqual({SimpleCell('usr/block/created'),
                          SimpleCell('usr/block/renamed2'),
                          SimpleCell('usr/block/modified_cell', CPP),
                          SimpleCell('usr/block/modified_both', CPP)}, set(p.cells))
        self.assertEqual({'created': Content(id_=None, load=Blob('created')),
                          'modified_cont': Content(id_=None, load=Blob('mod_content2')),
                          'modified_both': Content(id_=None, load=Blob('mod_both2'))}, p.contents)
        self.assertEqual({'renamed2': ID((1234,))}, p.contents_ids)

    def test_nonzero_one_file_content(self):
        changes = Changes()
        changes.modified['modified_cont'] = Modification(
                                                    Resource(SimpleCell('usr/block/pretty.js'),
                                                             Content(id_=None, load=Blob('mod_content'))),
                                                    Resource(SimpleCell('usr/block/pretty.js'),
                                                             Content(id_=None, load=Blob('mod_content2'))))
        p = PublishRequest(BlockVersion.loads('usr/block: 3'))
        p.msg = "Test Msg"
        p.changes = changes
        self.assertTrue(bool(p))

    def test_serialize(self):
        p = PublishRequest(BlockVersion.loads('usr/block: 3'))
        p.msg = "Test Msg"
        p.changes = self._changes()
        serial = p.serialize()
        p2 = PublishRequest.deserialize(serial)
        self.assertEqual(p.parent, p2.parent)
        self.assertEqual(p.tag, p2.tag)
        self.assertEqual(p.msg, p2.msg)
        self.assert_bii_equal(p.cells, p2.cells)
        self.assertEqual(p.contents, p2.contents)
        self.assertEqual(p.contents_ids, p2.contents_ids)
        self.assertEqual(p.deleted, p2.deleted)
        self.assertEqual(p.renames, p2.renames)
