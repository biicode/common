from biicode.common.settings.version import Version
from biicode.common.settings.tool_info import ToolInfo
from biicode.common.settings.fixed_string import FixedString
import copy
from biicode.common.settings.tools import Architecture
import platform
import os


class OSFamily(FixedString):
    values = {'Windows', 'Linux', 'MacOS', 'Java'}


class OSInfo(ToolInfo):
    """Store and capture information about running operating system."""

    smart_serial = copy.copy(ToolInfo.smart_serial)
    smart_serial['family'] = ('family', OSFamily, None)
    smart_serial['arch'] = ('arch', Architecture, None)

    platforms = {'windows': 'windows',
                 'win32':   'windows',
                 'linux':   'linux',
                 'linux2':  'linux',
                 'cygwin':  'linux',
                 'darwin':  'macos',
                 'os2':     'windows',
                 'os2emx':  'windows',
                 'riscos':  'linux',
                 'atheos':  'linux',
                 'java': 'java'
                 }

    @staticmethod
    def is_win():
        return OSInfo.family() == 'Windows'

    @staticmethod
    def is_mac():
        family = OSInfo.family()
        return family == 'MacOS'

    @staticmethod
    def is_linux():
        return OSInfo.family() == 'Linux'

    @staticmethod
    def is_debian_based_linux():
        if not OSInfo.is_linux():
            return False
        tmp = platform.linux_distribution()[0]
        return tmp == "debian" or tmp == "Ubuntu"

    @staticmethod
    def is_redhat_based_linux():
        if not OSInfo.is_linux():
            return False
        tmp = platform.linux_distribution()[0]
        return tmp == "Fedora" or tmp == "CentOS"

    @staticmethod
    def is_rpi():
        return 'arm' == os.uname()[4][:3]

    @staticmethod
    def family():
        os = platform.system().lower()
        return OSFamily(OSInfo.platforms[os])

    @staticmethod
    def architecture():
        return Architecture(platform.architecture()[0].lower())



    @staticmethod
    def capture():
        """ Capture current OS information
        """
        result = OSInfo()
        result.family = OSInfo.family()

        if result.family == 'windows':
            # i.e: subfamily = '7', version = "6.66612"
            result.subfamily = platform.release()
            result.version = Version(platform.version())

        elif result.family == 'linux':
            result.subfamily = platform.linux_distribution()[0]
            result.version = Version(platform.linux_distribution()[1])

        elif result.family == 'macos':
            result.subfamily = None
            result.version = Version(platform.mac_ver()[0])

        elif result.family == 'java':
            result.subfamily = " ".join(platform.java_ver()[2])
            result.version = Version(platform.release())

        else:
            result.subfamily = None  # Default value is none in ToolInfo
            result.version = Version()  # Default value is Version() in ToolInfo

        result.arch = OSInfo.architecture()
        return result
