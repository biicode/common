from biicode.common.test.bii_test_case import BiiTestCase
from nose.core import run
from biicode.common.test import model_creator as mother
from biicode.common.edition.processors.parse_processor import ParseProcessor
from biicode.common.model.bii_type import CPP
from biicode.common.output_stream import OutputStream
from biicode.common.model.blob import Blob
from biicode.common.model.resource import Resource
from biicode.common.model.cells import SimpleCell
from biicode.common.model.content import Content


class ParseProcessorTest(BiiTestCase):

    def test_has_main_and_dependency_declarations(self):
        processor = ParseProcessor()
        block_holder = mother.get_block_holder(['user/geom/main.cpp'], CPP)
        processor.do_process(block_holder, OutputStream())
        main = block_holder['main.cpp'].cell
        self.assertTrue(main.hasMain, 'Main method not detected by parse processor')
        self.check_dependency_set(main.dependencies, unresolved=['iostream', 'sphere.h'])

        # now remove #include
        load = block_holder['main.cpp'].content.load.bytes
        load = load.replace('#include "sphere.h"', '')
        block_holder.add_resource(Resource(SimpleCell('user/geom/main.cpp', CPP),
                                           Content('user/geom/main.cpp', Blob(load))))
        processor.do_process(block_holder, OutputStream())
        main = block_holder['main.cpp'].cell
        self.check_dependency_set(main.dependencies, unresolved=['iostream'])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    run()
