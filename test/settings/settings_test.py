import unittest
from biicode.common.settings.settings import Settings
import copy
from biicode.common.settings.tools import Builder


class SettingsTest(unittest.TestCase):

    def test_copy(self):
        s = Settings()
        s.cpp.builder = Builder(family='make')
        s2 = copy.deepcopy(s.cpp)
        self.assertEqual(s.cpp, s2)


if __name__ == "__main__":
    a = Settings.loads("{cpp: {kk: aux}}")
    print a.kk
