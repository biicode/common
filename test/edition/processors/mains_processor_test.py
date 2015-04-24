from unittest import TestCase
from biicode.common.edition.processors.main_config_processor import MainConfigProcessor
from biicode.common.edition.processors.parse_processor import ParseProcessor
from biicode.common.model.blob import Blob
from biicode.common.model.cells import SimpleCell
from biicode.common.model.content import Content
from biicode.common.test.edition.processors.helpers import process_holder
from biicode.common.model.resource import Resource
from biicode.common.edition.block_holder import BlockHolder, BIICODE_FILE
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.bii_type import CPP


class MainsProcessorTest(TestCase):
    def test_config_file_with_main(self):
        main_conf = 'r1.h'
        self.prepare_context(main_conf)
        process_holder(self.block_holder, self.processor)
        # Checks
        self.assertTrue(self.res['user/block/r1.h'].cell.hasMain)
        self.assertFalse(self.res['user/block/r2.cpp'].cell.hasMain)

    def test_config_unknown_file_main(self):
        main_conf = r'''r90.h'''
        self.prepare_context(main_conf)
        response = process_holder(self.block_holder, self.processor)
        # Checks
        self.assertIn("user/block mains: there aren't any matches with r90.h filter",
                      str(response))
        self.assertFalse(self.res['user/block/r1.h'].cell.hasMain)
        self.assertFalse(self.res['user/block/r2.cpp'].cell.hasMain)

    def test_config_unknown_file_with_main(self):
        main_conf = r'''r90.h
        r1.h'''
        self.prepare_context(main_conf)
        response = process_holder(self.block_holder, self.processor)
        # Checks
        self.assertIn("user/block mains: there aren't any matches with r90.h filter",
                      str(response))
        self.assertTrue(self.res['user/block/r1.h'].cell.hasMain)
        self.assertFalse(self.res['user/block/r2.cpp'].cell.hasMain)

    def test_delete_main(self):
        r1 = SimpleCell('user/block/r1.h', CPP)
        r2 = SimpleCell('user/block/r2.cpp', CPP)
        r3 = SimpleCell('user/block/r3.cpp', CPP)
        r4 = SimpleCell('user/block/' + BIICODE_FILE)

        res = {r1.name: Resource(r1, Content(None, Blob(''))),
               r2.name: Resource(r2, Content(None, Blob(''))),
               r3.name: Resource(r3, Content(None, Blob('int main(char* argv){}'))),
               r4.name: Resource(r4, Content(None, Blob('[mains]\n !r3.cpp')))}

        block_holder = BlockHolder(BlockName('user/block'), res)

        process_holder(block_holder, ParseProcessor())
        self.assertTrue(res['user/block/r3.cpp'].cell.hasMain)

        process_holder(block_holder, MainConfigProcessor())
        # Checks
        self.assertFalse(res['user/block/r1.h'].cell.hasMain)
        self.assertFalse(res['user/block/r2.cpp'].cell.hasMain)
        self.assertFalse(res['user/block/r3.cpp'].cell.hasMain)

    def test_mains_with_filter(self):
        r1 = SimpleCell('user/block/r1.h', CPP)
        r2 = SimpleCell('user/block/r2.cpp', CPP)
        r3 = SimpleCell('user/block/no_mains/r3.cpp', CPP)
        r4 = SimpleCell('user/block/no_mains/r4.cpp', CPP)
        r5 = SimpleCell('user/block/' + BIICODE_FILE)
        r6 = SimpleCell('user/block/new_mains/r6.cpp', CPP)
        r7 = SimpleCell('user/block/new_mains/r7.cpp', CPP)
        r8 = SimpleCell('user/block/exe_file1.hh', CPP)
        r9 = SimpleCell('user/block/exe_file2.hh', CPP)

        res = {r1.name: Resource(r1, Content(None, Blob(''))),
               r2.name: Resource(r2, Content(None, Blob(''))),
               r3.name: Resource(r3, Content(None, Blob('int main(char* argv){}'))),
               r4.name: Resource(r4, Content(None, Blob('int main(char* argv){}'))),
               r5.name: Resource(r5, Content(None, Blob('[mains]\n!no_mains/*\nnew_mains/*\n*.hh'))),
               r6.name: Resource(r6, Content(None, Blob(''))),
               r7.name: Resource(r7, Content(None, Blob(''))),
               r8.name: Resource(r8, Content(None, Blob(''))),
               r9.name: Resource(r9, Content(None, Blob('')))
               }

        block_holder = BlockHolder(BlockName('user/block'), res)

        process_holder(block_holder, ParseProcessor())
        self.assertTrue(res['user/block/no_mains/r3.cpp'].cell.hasMain)
        self.assertTrue(res['user/block/no_mains/r4.cpp'].cell.hasMain)
        self.assertFalse(res['user/block/new_mains/r6.cpp'].cell.hasMain)
        self.assertFalse(res['user/block/new_mains/r7.cpp'].cell.hasMain)
        self.assertFalse(res['user/block/exe_file1.hh'].cell.hasMain)
        self.assertFalse(res['user/block/exe_file2.hh'].cell.hasMain)

        process_holder(block_holder, MainConfigProcessor())

        # Checks
        self.assertFalse(res['user/block/r1.h'].cell.hasMain)
        self.assertFalse(res['user/block/r2.cpp'].cell.hasMain)
        self.assertFalse(res['user/block/no_mains/r3.cpp'].cell.hasMain)
        self.assertFalse(res['user/block/no_mains/r4.cpp'].cell.hasMain)
        self.assertTrue(res['user/block/new_mains/r6.cpp'].cell.hasMain)
        self.assertTrue(res['user/block/new_mains/r7.cpp'].cell.hasMain)
        self.assertTrue(res['user/block/exe_file1.hh'].cell.hasMain)
        self.assertTrue(res['user/block/exe_file2.hh'].cell.hasMain)

    def prepare_context(self, config):
        r1 = SimpleCell('user/block/r1.h')
        r2 = SimpleCell('user/block/r2.cpp')
        r3 = SimpleCell('user/block2/r3.cpp')
        r4 = SimpleCell('user/block/' + BIICODE_FILE)

        self.res = {r1.name: Resource(r1, None),
                    r2.name: Resource(r2, None),
                    r3.name: Resource(r3, None),
                    r4.name: Resource(r4, Content(None, Blob("[mains]\n" + config)))}

        self.block_holder = BlockHolder(BlockName('user/block'), self.res)
        self.processor = MainConfigProcessor()
