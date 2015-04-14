from biicode.common.settings.osinfo import OSInfo
from biicode.common.settings.cppsettings import CPPSettings
from biicode.common.settings.lang_settings import LanguageSettings
from biicode.common.settings.smart_serial import smart_serialize, smart_deserialize
from biicode.common.utils.serializer import DictDeserializer
from biicode.common.settings.loader import yaml_dumps, yaml_loads
from biicode.common.settings.rpisettings import RPiSettings
from biicode.common.settings.arduinosettings import ArduinoSettings
from yaml.scanner import ScannerError
from biicode.common.exception import ConfigurationFileError
from biicode.common.settings.cmakesettings import CMakeSettings


class UserSettings(dict):
    def serialize(self):
        return dict(self)

    @staticmethod
    def deserialize(data):
        deserializer = DictDeserializer(str, str)
        return UserSettings(deserializer.deserialize(data))


class Settings(object):
    """Stores information relative to user settings.
       This information is loaded from the hive bii/settings.bii

      Attributes
      ----------
        os: OSInfo
            Represent Operating System information of current execution.
        cpp: CPPSettings
            Specific settings about C++ tools and settings to be used during compilation time.
        rpi: RPiSettings
            Specific settings about RPi tools and settings to be used during compilation time.
        arduino: ArduinoSettings
            Specific settings about Arduino tools and settings to be used during compilation time.
        node: LanguageSettings
            Generic settings about language tools.
        user: UserSettings
            Specific user settings.

      Parameters
      ----------
        os_info: OsInfo, optional

    """

    def __init__(self, os_info=None):
        self.os = os_info or OSInfo.capture()
        self.cmake = CMakeSettings()
        self.cpp = CPPSettings()
        self.rpi = RPiSettings()
        self.arduino = ArduinoSettings()
        self.node = LanguageSettings()
        self.fortran = LanguageSettings()
        self.python = LanguageSettings()
        self.user = UserSettings()

    def __repr__(self):
        return yaml_dumps(self)

    @classmethod
    def loads(cls, data):
        """Load Settings from a yaml file."""
        try:
            settings = yaml_loads(cls, data) or cls()
        except ScannerError as e:
            raise ConfigurationFileError(str(e))
        # Migration to 2.3 new toolchain settings. Remove July 2015
        if settings.cpp.generator:
            settings.cmake.generator = settings.cpp.generator
            settings.cpp = CPPSettings()
        if settings.arduino.generator:
            settings.cmake.generator = settings.arduino.generator
            settings.arduino.generator = None
        return settings

    def dumps(self):
        """Dump settings data to yaml file."""
        return yaml_dumps(self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
            and self.cmake == other.cmake \
            and self.cpp == other.cpp \
            and self.rpi == other.rpi \
            and self.arduino == other.arduino \
            and self.fortran == other.fortran \
            and self.os == other.os\
            and self.python == other.python \
            and self.node == other.node \
            and self.user == other.user

    def __ne__(self, other):
        return not self.__eq__(other)

    smart_serial = {'os': ('os', OSInfo, OSInfo),
                    'cmake': ('cmake', CMakeSettings, CMakeSettings),
                    'cpp': ('cpp', CPPSettings, CPPSettings),
                    'rpi': ('rpi', RPiSettings, RPiSettings),
                    'arduino': ('arduino', ArduinoSettings, ArduinoSettings),
                    'fortran': ('fortran', LanguageSettings, LanguageSettings),
                    'python': ('python', LanguageSettings, LanguageSettings),
                    'node': ('node', LanguageSettings, LanguageSettings),
                    'user': ('user', UserSettings, UserSettings)}

    def serialize(self):
        return smart_serialize(self)

    @classmethod
    def deserialize(cls, data):
        if data is None:
            return None
        return smart_deserialize(cls, data)

    serialize_dict = serialize
    deserialize_dict = deserialize
