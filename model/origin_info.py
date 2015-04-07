from collections import namedtuple


class OriginInfo(namedtuple('OriginInfo', ['url', 'branch', 'tag', 'commit'])):
    '''
    Remote version control system information, including branch, tag or commit.
    It belongs to BlockDelta, so each version has its origin remote information
    linking VCS code with the biicode published version.
    '''

    def serialize(self):
        return (self.url, self.branch, self.tag, self.commit)

    @staticmethod
    def deserialize(doc):
        if doc is None:
            return None
        return OriginInfo(doc[0], doc[1], doc[2], doc[3])

    def __repr__(self):
        ret = "%s " % self.url
        if self.branch:
            ret += "(%s) " % self.branch
        if self.commit:
            ret += "@%s " % self.commit
        if self.tag:
            ret += "#%s" % self.tag
        return ret
