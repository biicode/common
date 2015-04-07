import unittest

from biicode.common.model.cells import CellDeserializer, VirtualCell
from biicode.common.settings.settings import Settings
from biicode.common.settings.osinfo import OSFamily
from biicode.common.model.brl.block_cell_name import BlockCellName


class VirtualResourceTest(unittest.TestCase):
    def setUp(self):
        funcion = 'def virtual(settings):\n\tif(settings.os.family == "windows"):return "win"\n\telse: return "nix"'
        self.r = VirtualCell('user/module/path/to/file.h', funcion)

    def testBasic(self):
        s = Settings()
        s.os.family = OSFamily('Linux')
        self.assertEqual('user/module/path/to/nix/file.h', self.r.evaluate(s))
        s.os.family = OSFamily('Windows')
        self.assertEqual('user/module/path/to/win/file.h', self.r.evaluate(s))
        #print self.r.leaves

    def testSerialize(self):
        serial = self.r.serialize()
        d = CellDeserializer(BlockCellName)
        deserialized = d.deserialize(serial)
        self.assertEquals(self.r, deserialized)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
