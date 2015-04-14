from collections import namedtuple
from biicode.common.utils.serializer import Serializer, DictDeserializer
from biicode.common.model.renames import Renames


Modification = namedtuple('Modification', ['old', 'new'])


class ModificationDeserializer(object):
    def __init__(self, values_deserializer):
        self.values_deserializer = values_deserializer

    def deserialize(self, data):
        """From dictionary to object Modification"""
        if callable(getattr(self.values_deserializer, "deserialize", None)):
            return Modification(self.values_deserializer.deserialize(data[0]),
                            self.values_deserializer.deserialize(data[1]))
        else:
            return Modification(self.values_deserializer(data[0]),
                            self.values_deserializer(data[1]))


class Changes(object):
    """ Generic class for Changes. keys and values in dicts can be anything """

    SERIAL_DELETED_KEY = "d"
    SERIAL_CREATED_KEY = "c"
    SERIAL_MODIFIED_KEY = "m"
    SERIAL_RENAMES_KEY = "r"
    SERIAL_SIMLIMIT_KEY = "s"

    def __init__(self):
        self.deleted = {}
        """dict of deleted {ID: Object} where object can be the diff, None if not necessary"""
        self.created = {}
        """dict {ID: Object} Where Value can be either a Cell, a Content or a Resource"""
        self.modified = {}
        """dict {ID: Modification} ID is the OldID in case of Rename."""
        self.renames = Renames()
        """dict {oldID: newID}"""
        self.sim_limit = 0.75

    def add_deleted(self, ID, value=None):
        """Value represents the old content """
        self.deleted[ID] = value

    def remove_deleted(self, ID):
        """useful when applying renames. Returns the old value, that MUST exist"""
        value = self.deleted[ID]
        del self.deleted[ID]
        return value

    def add_created(self, ID, value):
        """Value can be either a Cell, a Content or a Resource"""
        self.created[ID] = value

    def remove_created(self, ID):
        """useful when applying renames. Returns the old value, that MUST exist"""
        value = self.created[ID]
        del self.created[ID]
        return value

    def add_rename(self, old_name, new_name):
        self.renames[old_name] = new_name

    def remove_rename(self, ID):
        """useful when applying renames. Returns the old value, that MUST exist"""
        value = self.renames[ID]
        del self.renames[ID]
        return value

    def add_modified(self, ID, value):
        """Value can be either a Cell, a Content or a Resource"""
        self.modified[ID] = value

    def remove_modified(self, name):
        """useful for deleting big resources not allowed to be pushed to biicode"""
        del self.modified[name]

    def __len__(self):
        return len(self.modified) + len(self.deleted) + len(self.created)

    def __repr__(self):
        builder = []
        builder.append('Deleted %s' % str(self.deleted.keys()))
        builder.append('Created %s' % str(self.created.keys()))
        builder.append('Modified %s' % str(self.modified.keys()))
        builder.append('Renames %s' % str(self.renames))
        return '\n'.join(builder)

    def deduce_renames(self):
        renames = Renames()
        for created_key, created_value in self.created.iteritems():
            if hasattr(created_value, 'similarity'):
                max_sim, max_key = 0.0, None
                for deleted_key, deleted_value in self.deleted.iteritems():
                    sim = created_value.similarity(deleted_value)
                    if sim > max_sim:
                        max_sim, max_key = sim, deleted_key

                if max_sim > self.sim_limit:
                    renames[max_key] = created_key

        self.renames = renames

    def serialize(self):
        ret = Serializer().build(
              (Changes.SERIAL_DELETED_KEY,  self.deleted),
              (Changes.SERIAL_CREATED_KEY,  self.created),
              (Changes.SERIAL_MODIFIED_KEY, self.modified),
              (Changes.SERIAL_RENAMES_KEY,  self.renames),
              (Changes.SERIAL_SIMLIMIT_KEY, self.sim_limit),
        )
        return ret


class ChangesDeserializer(object):
    def __init__(self, keys_deserializer, values_deserializer):
        self.keys_deserializer = keys_deserializer
        self.values_deserializer = values_deserializer
        self.dict_values_deserializer = DictDeserializer(keys_deserializer, values_deserializer)

    def deserialize(self, data, kls=None):
        """From dictionary to object Changes"""
        kls = kls or Changes
        #NOTE: ID always is CellName, and values are text tuples, if not, we cant deserialize
        ret = kls()
        ret.deleted = self.dict_values_deserializer.deserialize(data[Changes.SERIAL_DELETED_KEY])
        renames_deserializer = DictDeserializer(self.keys_deserializer, self.keys_deserializer)
        ret.renames = renames_deserializer.deserialize(data[Changes.SERIAL_RENAMES_KEY])
        ret.created = self.dict_values_deserializer.deserialize(data[Changes.SERIAL_CREATED_KEY])
        #ret.modified = self.values_deserializer.deserialize(data[Changes.SERIAL_MODIFIED_KEY])
        mod_deserial = DictDeserializer(self.keys_deserializer,
                                        ModificationDeserializer(self.values_deserializer))
        ret.modified = mod_deserial.deserialize(data[Changes.SERIAL_MODIFIED_KEY])
        ret.sim_limit = data[Changes.SERIAL_SIMLIMIT_KEY]
        return ret
