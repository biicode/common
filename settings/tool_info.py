
from biicode.common.settings.version import Version
from biicode.common.settings.loader import yaml_dumps
from biicode.common.settings.smart_serial import smart_serialize, smart_deserialize


class ToolInfo(object):
    """ Store information about any tool, from a compiler to an Operating System.

        Attributes
        ----------
            family: something as Visual, CMake, Eclipse, Windows... could be FixedString
            subfamily: something as CDT (could be FixedString)
            version: Version
            code: codename, eg. 2008 for visual, or Karmic Koala for Ubuntu.
            arch: architecture: x64, ARM, etc
    """

    def __init__(self, family=None, subfamily=None, version=None, code=None, arch=None):
        """ Init a new ToolInfo object
            Arguments are all optional
        """
        self.family = family
        self.subfamily = subfamily
        self.version = version or Version()
        self.code = code
        self.arch = arch

    def __nonzero__(self):
        if self.family or self.subfamily or self.version or self.code or self.arch:
            return True
        return False

    smart_serial = {'family': ('family', None, None),
                    'subfamily': ('subfamily', None, None),
                    'version': ('version', Version, Version),
                    'code': ('code', None, None),
                    'arch': ('arch', None, None)}

    def serialize(self):
        return smart_serialize(self)

    @classmethod
    def deserialize(cls, data):
        d = smart_deserialize(cls, data)
        return d

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) and \
                   self.family == other.family and \
                   self.subfamily == other.subfamily and \
                   self.version == other.version and \
                   self.code == other.code and \
                   self.arch == other.arch

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return yaml_dumps(self)

    serialize_dict = serialize
    deserialize_dict = deserialize
