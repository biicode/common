from biicode.common.settings.osinfo import OSInfo
from biicode.common.settings.version import Version
import platform
import unittest


class OSinfo_Test(unittest.TestCase):

    def test_os_local_info(self):
        #TODO test this on different os
        os_info = OSInfo.capture()

        os = platform.system().lower()
        family = OSInfo.platforms.get(os)
        self.assertEquals(os_info.family, family)
        if family == 'linux':
            subfamily = platform.linux_distribution()[0]
            version = Version(platform.linux_distribution()[1])
        elif family == 'windows':
            subfamily = platform.release()
            version = Version(platform.version())
        elif family == 'macos':
            subfamily = None
            version = Version(platform.mac_ver()[0])
        else:
            subfamily = ""
            version = ""

        self.assertEquals(os_info.subfamily, subfamily)
        self.assertEquals(os_info.version, version)
