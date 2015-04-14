from biicode.common.settings.cppsettings import CPPSettings
from biicode.common.settings.settings import Settings
import unittest
from biicode.common.settings.loader import yaml_loads


class SettingsSerializationTest(unittest.TestCase):
    def test_load_cpp_settings(self):
        expected = '''
compiler:
  family: GNU
  version: 3.4.1
builder:
  family: MAKE
  version: 3.4.1
generator: Visual Studio 2008
defines:
  NO_BUILD: 1
'''
        cpp = yaml_loads(CPPSettings, expected)
        self.assertEqual(cpp.generator, 'Visual Studio 2008')

    def test_user_defined_settings(self):
        raw_settings = '''cmake: {generator: Visual}
os: {arch: 64bit, family: MacOS, version: 10.9.1}
user: {my_definition: hola, my_other_definition: adios}
'''
        settings = Settings.loads(raw_settings)
        self.assertTrue(hasattr(settings, 'user'))
        self.assertIn('my_definition', settings.user)
        self.assertEquals('hola', settings.user['my_definition'])
        self.assertEquals('adios', settings.user['my_other_definition'])

        dump = settings.dumps()
        self.assertEquals(raw_settings, dump)
