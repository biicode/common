from biicode.common.settings.smart_serial import smart_serialize, smart_deserialize
from biicode.common.exception import ConfigurationFileError
import os
from biicode.common.settings.loader import yaml_dumps


class CMakeSettings(object):
    """ Store specific CMake settings
    """
    def __init__(self):
        self.generator = None
        self.toolchain = None

    def __nonzero__(self):
        return True if self.generator or self.toolchain else False

    def serialize(self):
        serial = smart_serialize(self)
        return serial

    @classmethod
    def deserialize(cls, data):
        try:
            d = smart_deserialize(cls, data)
        except ValueError as error:
            raise ConfigurationFileError("Error parsing settings.bii %s %s" % (os.linesep, error))
        return d

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) \
            and self.generator == other.generator \
            and self.toolchain == other.toolchain

    def __ne__(self, other):
        return not self.__eq__(other)

    smart_serial = {'generator': ('generator', None, None),
                    'toolchain': ('toolchain', None, None)}

    def __repr__(self):
        return yaml_dumps(self)

    serialize_dict = serialize
    deserialize_dict = deserialize
