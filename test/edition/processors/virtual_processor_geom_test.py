import unittest
from nose.core import run
from biicode.common.model.cells import SimpleCell, VirtualCell
from biicode.common.edition.processors.virtual_processor import VirtualConfigurationProcessor
from biicode.common.settings.settings import Settings
from biicode.common.model.bii_type import CPP
from biicode.common.test import model_creator as mother
from biicode.common.output_stream import OutputStream


class VirtualProcessorGeomTest(unittest.TestCase):

    def test_basic_geom(self):
        block_cell_names = mother.make_folder_resources('dummy', 'virtual')
        self.block_holder = mother.get_block_holder(block_cell_names, CPP)

        VirtualConfigurationProcessor().do_process(self.block_holder, OutputStream())
        self.assertEqual(8, len(self.block_holder.cell_names))

        self.check_virtual_resource('sphere.cpp')
        self.check_virtual_resource('sphere.h')

    def check_virtual_resource(self, name):
        vsphere = self.block_holder[name].cell

        self.assertTrue(isinstance(vsphere, VirtualCell))
        self.check_virtual_options(name, vsphere)
        self.check_simple_realizations(name, vsphere)

    def check_simple_realizations(self, name, vsphere):
        devsphere = self.block_holder['develop/%s' % name].cell
        self.assertTrue(isinstance(devsphere, SimpleCell))
        self.assertEqual(devsphere.container, vsphere.name)

        testsphere = self.block_holder['test/%s' % name].cell
        self.assertTrue(isinstance(testsphere, SimpleCell))
        self.assertEqual(testsphere.container, vsphere.name)

    def check_virtual_options(self, name, vsphere):
        self.assertEqual(set(['test', 'develop']), vsphere.leaves)
        self.assertEqual(set(['dummy/virtual/test/%s' % name,
                              'dummy/virtual/develop/%s' % name]),
                         set(vsphere.resource_leaves))
        settings = Settings()
        settings.user['test'] = False
        self.assertEqual('dummy/virtual/develop/%s' % name, vsphere.evaluate(settings))

        settings.user['test'] = True
        self.assertEqual('dummy/virtual/test/%s' % name, vsphere.evaluate(settings))


if __name__ == "__main__":
    run()
