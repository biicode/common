from biicode.common.model.renames import Renames
from biicode.common.model.id import ID
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.cells import CellDeserializer
from biicode.common.utils.serializer import ListDeserializer, Serializer, DictDeserializer
from biicode.common.model.brl.cell_name import CellName
from biicode.common.model.content import ContentDeserializer
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.model.version_tag import VersionTag, DEV
from biicode.common.model.origin_info import OriginInfo


class PublishRequest(object):
    '''
    This class wraps all the information that is necessary to publish things in
    biicode. It is computed in the client, and handled in the server by the PublishService
    '''

    def __init__(self, parent=None):
        self.parent = parent  # BlockVersion, the one to compute the changes
        self.parent_time = None  # DateTime of the parent publication, obtained from Delta
        # self._changes = None  # Transient Changes object
        self.msg = ""
        self.tag = DEV
        self.versiontag = None
        self.deptable = None
        # Internal status, deducible from changes
        self.cells = []  # [] of cells
        self.deleted = []  # [] of cell_names
        self.contents = {}  # {CellName: Content}
        self.contents_ids = {}  # {CellName: ContentID}
        self.renames = Renames()
        self.origin = None
        self._bytes = None

    @property
    def bytes(self):
        if not self._bytes:
            self._bytes = sum([content.load.size
                               for content in self.contents.itervalues() if content])

        return self._bytes

    @property
    def block_name(self):
        return self.parent.block_name

    @property
    def changes(self):
        raise NotImplementedError("No getter here")

    @changes.setter
    def changes(self, changes):
        """Changes of {Cellname: (Cell, Content)}"""
        self.cells = []
        self.deleted = []
        self.contents = {}
        self.contents_ids = {}
        # self._changes = changes
        self._add_created_and_modified(changes)
        self._add_deleted(changes)
        self.renames = changes.renames

    def _add_created_and_modified(self, changes):
        for name, (cell, content) in changes.created.iteritems():
            if cell:
                self.cells.append(cell)
            if content:
                content.parser = None  # Do not publish parsing info
                content._is_parsed = False
                self.contents[name] = content

        for name, ((old_cell, old_content), (cell, content)) in changes.modified.iteritems():
            if old_cell != cell:
                self.cells.append(cell)
            if old_content != content:
                if content is not None:
                    content.parser = None  # Do not publish parsing info
                    content._is_parsed = False
                self.contents[name] = content

    def _add_deleted(self, changes):
        for cell_name, (_, old_content) in changes.deleted.iteritems():
            self.deleted.append(cell_name)
            #Check if renames without changes, to upload only content ID
            new_name = changes.renames.get(cell_name)
            if new_name:
                new_content = self.contents[new_name]
                if new_content == old_content:
                    del self.contents[new_name]
                    self.contents_ids[new_name] = old_content.ID

    def __nonzero__(self):
        if self.cells or self.contents or self.deleted or self.contents_ids:
            return True
        return False

    def __repr__(self):
        header = ("PublishRequest: Parent: %s\n" % self.parent.to_pretty())
        return header

    SERIAL_TRACKED_KEY = "t"
    SERIAL_PARENT_DATETIME = "dt"
    SERIAL_TAG_KEY = "tg"
    SERIAL_VTAG_KEY = "vt"
    SERIAL_MSG_KEY = "ms"
    SERIAL_CELLS_KEY = "r"
    SERIAL_CONTENTS_KEY = "c"
    SERIAL_CONTENTS_ID_KEY = "ci"
    SERIAL_DELETED_KEY = "d"
    SERIAL_RENAMES_KEY = "m"
    SERIAL_DEP_TABLE = 'dep'
    SERIAL_ORIGIN_INFO = 'o'

    @staticmethod
    def deserialize(data):
        '''From dictionary to object Publish Pack'''
        pp = PublishRequest()
        pp.parent = BlockVersion.deserialize(data[PublishRequest.SERIAL_TRACKED_KEY])
        pp.parent_time = data[PublishRequest.SERIAL_PARENT_DATETIME]
        pp.tag = VersionTag.deserialize(data[PublishRequest.SERIAL_TAG_KEY])
        pp.msg = data[PublishRequest.SERIAL_MSG_KEY]
        # Backward client compatibility
        pp.versiontag = data.get(PublishRequest.SERIAL_VTAG_KEY, None)
        pp.deptable = BlockVersionTable.deserialize(data[PublishRequest.SERIAL_DEP_TABLE])
        pp.cells = ListDeserializer(CellDeserializer(BlockCellName)).\
                            deserialize(data[PublishRequest.SERIAL_CELLS_KEY])
        pp.deleted = ListDeserializer(CellName).\
                            deserialize(data[PublishRequest.SERIAL_DELETED_KEY])
        pp.renames = Renames.deserialize(data[PublishRequest.SERIAL_RENAMES_KEY])
        pp.contents = DictDeserializer(CellName, ContentDeserializer(BlockCellName)).\
                        deserialize(data[PublishRequest.SERIAL_CONTENTS_KEY])
        pp.contents_ids = DictDeserializer(CellName, ID).\
                            deserialize(data[PublishRequest.SERIAL_CONTENTS_ID_KEY])
        # Backward client compatibility
        pp.origin = OriginInfo.deserialize(data.get(PublishRequest.SERIAL_ORIGIN_INFO, None))
        return pp

    def serialize(self):
        for c in self.contents.itervalues():
            if c is not None:
                c.load.serialize_bytes = True
        ret = Serializer().build(
                 (PublishRequest.SERIAL_TRACKED_KEY, self.parent),
                 (PublishRequest.SERIAL_PARENT_DATETIME, self.parent_time),
                 (PublishRequest.SERIAL_TAG_KEY, self.tag),
                 (PublishRequest.SERIAL_MSG_KEY, self.msg),
                 (PublishRequest.SERIAL_VTAG_KEY, self.versiontag),
                 (PublishRequest.SERIAL_CELLS_KEY, self.cells),
                 (PublishRequest.SERIAL_CONTENTS_KEY, self.contents),
                 (PublishRequest.SERIAL_DELETED_KEY, self.deleted),
                 (PublishRequest.SERIAL_RENAMES_KEY, self.renames),
                 (PublishRequest.SERIAL_DEP_TABLE, self.deptable),
                 (PublishRequest.SERIAL_CONTENTS_ID_KEY, self.contents_ids),
                 (PublishRequest.SERIAL_ORIGIN_INFO, self.origin),
              )
        return ret
