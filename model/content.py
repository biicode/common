#!/usr/bin/env python
# package: com.biicode.model

from biicode.common.exception import BiiSerializationException
from biicode.common.model.declare.declaration import Declaration
from biicode.common.diffmerge.differ import text_unified_diff
from biicode.common.utils.serializer import Serializer
from biicode.common.model.blob import Blob
from biicode.common.edition.parsing.parser import Parser


def content_diff(base, other, baseName='base', otherName='other'):
    if base:
        if base.load.is_binary:
            return 'Unable to diff binary contents of %s' % baseName
        textBase = base.load.bytes
    else:
        textBase = ""

    if other:
        if other.load.is_binary:
            return 'Unable to diff binary contents of %s' % baseName
        textOther = other.load.bytes
    else:
        textOther = ""
    if textBase == textOther:
        return ""
    return text_unified_diff(textBase, textOther, baseName, otherName)


class Content(object):
    """ manages real contents of data as binary data (i.e. files etc.)"""

    SERIAL_ID_KEY = "_id"
    SERIAL_LOAD_KEY = "l"
    SERIAL_PARSER_KEY = "p"
    SERIAL_IS_PARSED_KEY = "i"

    def __init__(self, id_, load, parser=None, is_parsed=False, created=False):
        self.ID = id_
        self._load = load
        self._parser = parser
        self._is_parsed = is_parsed
        self._meta_updated = True
        self._blob_updated = created

    @property
    def meta_updated(self):
        return self._meta_updated

    @property
    def blob_updated(self):
        return self._blob_updated

    @property
    def parser(self):
        return self._parser

    @parser.setter
    def parser(self, p):
        self._parser = p
        self._is_parsed = False

    @property
    def load(self):
        return self._load

    @property
    def sha(self):
        return self._load.sha

    def set_blob(self, blob):
        """ setter bypassing invalidation of parser
        """
        self._load = blob

    def similarity(self, other):
        # published resource
        if self.ID is not None:
            if self.ID == other.ID:
                # it should be identical
                return 1.0
        return self._load.similarity(other._load)

    def __hash__(self):
        return hash(self._load)

    def __eq__(self, other):
        '''equality does NOT check for ID, 2 contents can be equal with different ID'''
        if self is other:
            return True
        return isinstance(other, self.__class__) and self._load == other._load

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        rep = "Content [Id=%s, load=%r]" % (self.ID, self._load)
        return rep

    def serialize(self):
        ret = Serializer().build(
              (Content.SERIAL_ID_KEY, self.ID),
              (Content.SERIAL_LOAD_KEY, self._load),
              (Content.SERIAL_PARSER_KEY, self._parser),
              (Content.SERIAL_IS_PARSED_KEY, self._is_parsed),
        )
        return ret

    def parse(self):
        if self._parser and not self._is_parsed:
            self._parser.parse(self._load.bytes)
            self._parser_updated = True
        self._is_parsed = True

    def update_content_declaration(self, decl, new_decl):
        # Now it is only used for version upgrades that involve a rename
        assert isinstance(decl, Declaration)
        assert isinstance(new_decl, Declaration)
        #if self._parser and new_decl:
        new_text = self._parser.updateDeclaration(self._load.bytes, decl, new_decl)
        if new_text:
            self._load = Blob(new_text)
            self._blob_updated = True
            self._parser_updated = True


class ContentDeserializer(object):
    def __init__(self, id_type):
        '''
        @param id_type BlockCellName or ID
        '''
        self.id_type = id_type

    def deserialize(self, data):
        '''From dictionary to object Content'''
        if data is None:
            return None
        try:
            content = Content(id_=self.id_type.deserialize(data[Content.SERIAL_ID_KEY]),
                           load=Blob.deserialize(data[Content.SERIAL_LOAD_KEY]),
                           parser=Parser.deserialize(data[Content.SERIAL_PARSER_KEY]),
                           is_parsed=data[Content.SERIAL_IS_PARSED_KEY],
                           )
            content._meta_updated = False
            return content
        except Exception as e:
            raise BiiSerializationException('Could not deserialize Content: %s' % str(e))
