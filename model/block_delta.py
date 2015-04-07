import datetime
from biicode.common.model.version_tag import VersionTag
from biicode.common.conf import DATETIME_FORMAT
from biicode.common.model.origin_info import OriginInfo


class BlockDelta(object):
    """ Basic information of a block delta (publication)"""

    def __init__(self, msg, tag, date, versiontag=None, origin=None, commiter=None):
        self.msg = msg  # string with publish message
        self.tag = tag  # DEV, ALPHA, BETA, STABLE
        self.versiontag = versiontag  # 1, 1.5.3...
        self.date = date  # a float object containing seconds of timestamp
        self.origin = origin
        self.commiter = commiter

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.date)

    @property
    def formatted_datetime(self):
        """getter for a formatted date and time"""
        dt = datetime.datetime.fromtimestamp(self.date)
        return dt.strftime(DATETIME_FORMAT)

    @property
    def formatted_date(self):
        """getter for a formatted date"""
        return self.formatted_datetime.split()[0]

    def serialize(self):
        '''serializer for block_delta'''
        return self.msg, self.tag.serialize(), self.date, \
            self.versiontag, self.origin, self.commiter

    @staticmethod
    def deserialize(doc):
        '''Block delta from serialized dictionary'''
        doc = list(doc)
        while(len(doc) < 6):  # Retrocompatibility with values serialized with not all parameters
            doc.append(None)
        return BlockDelta(doc[0],
                          VersionTag.deserialize(doc[1]),
                          doc[2],
                          doc[3],
                          OriginInfo.deserialize(doc[4]),
                          doc[5])  # Msg, tag, date #vtag

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) and self.msg == other.msg \
            and self.tag == other.tag and self.date == other.date \
            and self.commiter == other.commiter

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Msg: %s, tag: %s, date: %s, , commiter: %s" % (self.msg,
                                                               self.tag,
                                                               self.date,
                                                               self.commiter)
