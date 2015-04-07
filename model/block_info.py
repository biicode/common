from biicode.common.model.symbolic.block_version import BlockVersion


class BlockInfo(object):
    '''
    Contains block permissions for a certain user (assuming can_read == True)
    If block already exists it also contains it's last published version
    '''

    def __init__(self, can_write=False, last_version=None, private=False):
        #If cant read, you get a None BlockInfo
        self.can_write = can_write
        self.last_version = last_version
        self.private = private

    def serialize(self):
        return (self.can_write, self.last_version.serialize(), self.private)

    @staticmethod
    def deserialize(doc):
        return BlockInfo(doc[0], BlockVersion.deserialize(doc[1]), doc[2])

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) and self.can_write == other.can_write \
            and self.last_version == other.last_version and self.private == other.private

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return ("Writable: %s, Last version: %s, Private: %s"
                % (self.can_write, self.last_version, self.private))
