
from biicode.common.model.bii_type import BiiType
from biicode.common.settings.osinfo import OSInfo
from biicode.common.settings.version import Version
from biicode.common.utils.serializer import Serializer
from biicode.common.settings.tool_info import ToolInfo


class SystemID(object):
    """
    Identifies a set of symbols (System Resource Names) related to an specific implementation:
    The ID includes the following fields:
      NAME_ID:  symbolic name for referencing this set. For languages extensions is easy:
                i.e.: open_gl but for symbols related to the interpreter or the compiler could
                be a little confusing. i.e.: the standard imports included in a clean
                installation of CPYTHON in such cases, the name should be "built_in"
      VERSION_ID: the version number related to the item (in case of BUILT_IN, should be the
                 version of the TOOL)
      BIITYPE: CPP, PYTHON, JAVA, XML, ...
      LANGUAGE_VERSION: i.e: "1.6.0" for JAVA 1.6 or "98.0.0" for CPP or "2.7.4" for PYTHON 2.7.4,
                             empty version = ANY
      OS_INFO: os info were the data was retrieved
      TOOL_INFO: Info of the tool that uses this set of symbols. family, subfamily, version,
                 architecture is specially important for BUILT_IN symbols.
                 Go to the ToolInfo class description for details.
      PATH: [optional] base path used for retrieving this info
    """
    SERIAL_NAME_ID_KEY = "n_id"
    SERIAL_VERSION_ID_KEY = "v_id"
    SERIAL_BIITYPE_KEY = "bT"
    SERIAL_LANGUAGE_VERSION_KEY = "l_v"
    SERIAL_OS_INFO_KEY = "os_i"
    SERIAL_TOOL_INFO_KEY = "t_i"
    SERIAL_PATH_KEY = "p"

    def __init__(self, name_id, biiType, version_id=None, language_version=None, os_info=None,
                 tool_info=None, path=""):
        self.name_id = name_id
        self.biiType = biiType
        self.__version_id = version_id
        self.__language_version = language_version or Version()
        self.os_info = os_info or OSInfo()
        self.tool_info = tool_info or ToolInfo()
        self.path = path

    def set_generic_system(self):
        self.language_version = Version()
        self.os_info = OSInfo()

    @property
    def version_id(self):
        return self.__version_id

    @property
    def language_version(self):
        return self.__language_version

    @version_id.setter
    def version_id(self, version_id):
        assert isinstance(version_id, str)
        self.__version_id = Version(version_id)

    @language_version.setter
    def language_version(self, language_version):
        assert isinstance(language_version, str)
        self.__language_version = Version(language_version)

    def serialize(self):
        ret = Serializer().build(
              (SystemID.SERIAL_NAME_ID_KEY, self.name_id),
              (SystemID.SERIAL_VERSION_ID_KEY, self.version_id),
              (SystemID.SERIAL_BIITYPE_KEY, self.biiType),
              (SystemID.SERIAL_LANGUAGE_VERSION_KEY, self.language_version),
              (SystemID.SERIAL_OS_INFO_KEY, self.os_info),
              (SystemID.SERIAL_TOOL_INFO_KEY, self.tool_info),
              (SystemID.SERIAL_PATH_KEY, self.path)
              )
        return ret

    @staticmethod
    def deserialize(data):
        return SystemID(
            data[SystemID.SERIAL_NAME_ID_KEY],
            version_id=Version.deserialize(data[SystemID.SERIAL_VERSION_ID_KEY]),
            biiType=BiiType.deserialize(data[SystemID.SERIAL_BIITYPE_KEY]),
            language_version=Version.deserialize(data[SystemID.SERIAL_LANGUAGE_VERSION_KEY]),
            os_info=OSInfo.deserialize(data[SystemID.SERIAL_OS_INFO_KEY]),
            tool_info=ToolInfo.deserialize(data[SystemID.SERIAL_TOOL_INFO_KEY]),
            path=data[SystemID.SERIAL_PATH_KEY],
        )

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, self.__class__):
            return self.name_id == other.name_id and \
                   self.version_id == other.version_id and \
                   self.biiType == other.biiType and \
                   self.language_version == other.language_version and \
                   self.os_info == other.os_info and \
                   self.tool_info == other.tool_info and \
                   self.path == other.path
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
