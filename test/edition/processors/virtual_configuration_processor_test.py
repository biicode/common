from biicode.common.model.cells import SimpleCell, VirtualCell
from biicode.common.edition.processors.virtual_processor import VirtualConfigurationProcessor
from biicode.common.test.bii_test_case import BiiTestCase
from biicode.common.model.blob import Blob
from biicode.common.model.content import Content
from biicode.common.settings.settings import Settings
from biicode.common.settings.osinfo import OSInfo
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.resource import Resource
from biicode.common.model.brl.block_name import BlockName
from biicode.common.output_stream import OutputStream

myConf1 = '''
def func(settings):
    """sphere.h, sphere.cpp"""
    if(settings.os.family == "windows"):
        return "win"
    else:
        return "nix"
'''

myConf2 = '''
def func(settings):
    """sphere.h, sphere.cpp"""
    if(settings.os.family == "windows"):
        return "win"
'''

myConf3 = '''
def func2(settings):
    """cube.h"""
    if(settings.os.family == "linux"):
        return "linux"
    else:
        return "default"
'''


class VirtualConfigurationProcessorTest(BiiTestCase):

    def test_create_missing_simple_resources(self):
        resources = {'bii/virtual.bii': Resource(SimpleCell('user/block/bii/virtual.bii'),
                                                  Content(None, Blob(myConf1)))}
        self.block_holder = BlockHolder(BlockName('user/block'), resources)

        VirtualConfigurationProcessor().do_process(self.block_holder, OutputStream())

        self._sphere_os_checks('sphere.h')
        self._sphere_os_checks('sphere.cpp')

        self.assertEqual(None, self.block_holder['sphere.h'].content)
        self.assertEqual(None, self.block_holder['sphere.cpp'].content)

    def _sphere_os_checks(self, name):
        vsphere = self.block_holder[name].cell
        self.assertTrue(isinstance(vsphere, VirtualCell), '%s is not a VirtualCell' % vsphere.name)
        self.assertEqual(set(['win', 'nix']), vsphere.leaves)
        self.assertEqual(set(['user/block/win/%s' % name, 'user/block/nix/%s' % name]),
                         set(vsphere.resource_leaves))

        settings = Settings(OSInfo('linux'))
        self.assertEqual('user/block/nix/%s' % name, vsphere.evaluate(settings))

        settings = Settings(OSInfo('windows'))
        self.assertEqual('user/block/win/%s' % name, vsphere.evaluate(settings))

        winsphere = self.block_holder['win/%s' % name].cell
        self.assertTrue(isinstance(winsphere, SimpleCell))
        nixsphere = self.block_holder['nix/%s' % name].cell
        self.assertTrue(isinstance(nixsphere, SimpleCell))
