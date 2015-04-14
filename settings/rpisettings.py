from biicode.common.settings.smart_serial import smart_serialize, smart_deserialize
from biicode.common.settings.loader import yaml_dumps


class RPiSettings(object):
    """Generic class to store specific information needed to run a Raspberry Pi project.

        Attributes
        ----------
            user: user
                Store information about the user name of the Raspberry Pi OS.
            ip: ip
                Store information about the Raspberry Pi ip address.
            directory: directory
                Store information about the Raspberry Pi destiny directory.

    """

    def __init__(self, user=None, ip=None, directory=None):
        self.user = user
        self.ip = ip
        self.directory = directory

    def __nonzero__(self):
        if self.user or self.ip:
            return True
        return False

    smart_serial = {'user': ('user', None, None),
                    'ip': ('ip', None, None),
                    'directory': ('directory', None, None)}

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
                   self.user == other.user and \
                   self.ip == other.ip and \
                   self.directory == other.directory

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return yaml_dumps(self)

    serialize_dict = serialize
    deserialize_dict = deserialize
