import unittest
from biicode.common.model.bii_type import CPP
from biicode.common.model.cells import SimpleCell
from biicode.common.edition.processors.deps_configuration import DependenciesConfigurationProcessor
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.blob import Blob
from biicode.common.model.content import Content
from biicode.common.test.edition.processors.helpers import process_holder
from biicode.common.edition.block_holder import BlockHolder, BIICODE_FILE
from biicode.common.model.resource import Resource
from biicode.common.model.brl.block_name import BlockName
from biicode.common.output_stream import OutputStream


class DependencyConfigurationProcessorTest(unittest.TestCase):

    def _prepare_context(self, my_conf):
        if my_conf:
            my_conf = "[dependencies]\n " + my_conf
        self.processor = DependenciesConfigurationProcessor()
        self.r1 = BlockCellName('user/block/r1.h')
        self.r2 = BlockCellName('user/block/r2.cpp')
        self.r3 = BlockCellName('user/block/r3.cpp')
        r1 = SimpleCell(self.r1, CPP)
        r2 = SimpleCell(self.r2, CPP)
        r3 = SimpleCell('user/block/r3.cpp', CPP)

        r4 = SimpleCell('user/block/' + BIICODE_FILE)
        res = {r1.name: Resource(r1, Content(None, Blob("hi"))),
               r2.name: Resource(r2, Content(None, Blob("hi"))),
               r3.name: Resource(r3, Content(None, Blob("hi"))),
               r4.name: Resource(r4, Content(None, Blob(my_conf)))
              }
        return BlockHolder(BlockName('user/block'), res)

    def test_basic_add(self):
        my_conf = 'r1.h + r2.cpp'
        block_holder = self._prepare_context(my_conf)
        process_holder(block_holder, self.processor)

        r1 = block_holder[self.r1.cell_name].cell
        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        self.assertEqual({self.r2}, r1.dependencies.implicit)
        self.assertEqual(set(), r1.dependencies.exclude_from_build)

    def test_old_format_add_implicit(self):
        my_conf = 'r1.h r2.cpp'
        block_holder = self._prepare_context(my_conf)
        process_holder(block_holder, self.processor)

        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual({self.r2}, r1.dependencies.implicit)
        self.assertEqual(set(), r1.dependencies.exclude_from_build)

    def test_old_format_add_explicit(self):
        my_conf = '+r1.h r2.cpp'
        block_holder = self._prepare_context(my_conf)
        process_holder(block_holder, self.processor)

        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual({self.r2}, r1.dependencies.implicit)
        self.assertEqual(set(), r1.dependencies.exclude_from_build)

    def test_basic_remove(self,):
        my_conf = 'r1.h - r2.cpp'
        block_holder = self._prepare_context(my_conf)
        block_holder[self.r1.cell_name].cell.dependencies.implicit.add(self.r2)
        process_holder(block_holder, self.processor)

        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual(set(), r1.dependencies.implicit)
        self.assertEqual(set(), r1.dependencies.exclude_from_build)

    def test_old_format_remove(self,):
        my_conf = '-r1.h r2.cpp'
        block_holder = self._prepare_context(my_conf)
        block_holder[self.r1.cell_name].cell.dependencies.implicit.add(self.r2)
        process_holder(block_holder, self.processor)

        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual(set(), r1.dependencies.implicit)
        self.assertEqual(set(), r1.dependencies.exclude_from_build)

    def test_basic_assign(self,):
        my_conf = 'r1.h = r2.cpp'
        block_holder = self._prepare_context(my_conf)
        block_holder[self.r1.cell_name].cell.dependencies.implicit.add(self.r3)
        process_holder(block_holder, self.processor)

        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual({self.r2}, r1.dependencies.implicit)
        self.assertEqual(set(), r1.dependencies.exclude_from_build)

    def test_old_format_assign(self,):
        my_conf = '=r1.h r2.cpp'
        block_holder = self._prepare_context(my_conf)
        block_holder[self.r1.cell_name].cell.dependencies.implicit.add(self.r3)
        process_holder(block_holder, self.processor)

        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual({self.r2}, r1.dependencies.implicit)
        self.assertEqual(set(), r1.dependencies.exclude_from_build)

    def test_process_config_file_with_unknown_target(self):
        my_conf = '''r8.h + r2.cpp r3.cpp'''
        block_holder = self._prepare_context(my_conf)
        biiout = process_holder(block_holder, self.processor)
        self.assertIn('There are no files matching pattern r8.h', str(biiout))

    def test_process_config_file_with_unknown_deps(self):
        my_conf = '''r1.h + r9.cpp'''
        block_holder = self._prepare_context(my_conf)
        block_holder[self.r1.cell_name].cell.dependencies.implicit.add(self.r2)
        biiout = OutputStream()
        self.processor.do_process(block_holder, biiout)
        self.assertIn('There are no files matching pattern r9.cpp', str(biiout))
        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual({self.r2}, r1.dependencies.implicit)

    def test_process_config_file_with_other_block_dep(self):
        my_conf = '''r1.h + r23.cpp'''
        block_holder = self._prepare_context(my_conf)
        biiout = process_holder(block_holder, self.processor)
        self.assertIn('There are no files matching pattern r23.cpp', str(biiout))
        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual(set(), r1.dependencies.implicit)

    def test_process_config_file_with_wildcard(self):
        my_conf = '''* + r2.cpp'''
        block_holder = self._prepare_context(my_conf)
        process_holder(block_holder, self.processor)
        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        r1 = block_holder[self.r1.cell_name].cell
        self.assertEqual({self.r2}, r1.dependencies.implicit)
        r3 = block_holder[self.r3.cell_name].cell
        content = block_holder[self.r3.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        self.assertEqual({self.r2}, r3.dependencies.implicit)

    def test_process_config_file_with_partial_wildcard(self):
        my_conf = '''*1.h + r2.cpp r3.cpp'''
        block_holder = self._prepare_context(my_conf)
        process_holder(block_holder, self.processor)
        r1 = block_holder[self.r1.cell_name].cell
        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        self.assertEqual({self.r2, self.r3}, r1.dependencies.implicit)

    def test_process_config_file_with_partial_wildcard_and_cell_patterns(self):
        my_conf = '''*1.h + *.cpp r23.cpp'''
        block_holder = self._prepare_context(my_conf)
        biiout = process_holder(block_holder, self.processor)
        self.assertIn('There are no files matching pattern r23.cpp', str(biiout))
        r1 = block_holder[self.r1.cell_name].cell
        content = block_holder[self.r1.cell_name].content
        self.assertTrue(content.meta_updated)
        self.assertFalse(content.blob_updated)
        self.assertEqual({self.r2, self.r3}, r1.dependencies.implicit)
