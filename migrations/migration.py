from biicode.common.utils.serializer import Serializer


class Migration(object):
    """Migration of biicode. ID HAVE TO BE UNIQUE"""

    def __init__(self):
        self.ID = self.__class__.__name__
        # Applied at
        self.applied_timestamp = None

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, Migration) and \
            self.ID == other.ID \
            and self.applied_timestamp == other.applied_timestamp

    def __neq__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s - %s" % (self.ID, self.applied_timestamp)

    def __hash__(self):
        # the hash of our string is our unique hash
        return hash(self.ID)

    SERIAL_ID_KEY = "i"
    SERIAL_TIMESTAMP_KEY = "t"

    def serialize(self):
        '''serializer for migration.
        Needs a dict because its directly a mongo collectionS'''
        return Serializer().build(
                (Migration.SERIAL_ID_KEY, self.ID),
                (Migration.SERIAL_TIMESTAMP_KEY, self.applied_timestamp),
        )

    @classmethod
    def deserialize(kls, doc):
        '''Migration from serialized dictionary'''
        mig = kls()
        mig.ID = doc[Migration.SERIAL_ID_KEY]
        mig.applied_timestamp = doc[Migration.SERIAL_TIMESTAMP_KEY]
        return mig
