from biicode.common.test import model_creator as mother, testfileutils
from biicode.common.edition.processors.cpp_implementation import CPPImplementationsProcessor
from biicode.common.model.cells import SimpleCell
from biicode.common.model.bii_type import BiiType, CPP
from nose_parameterized import parameterized
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.blob import Blob
from biicode.common.model.content import Content
from biicode.common.edition.parsing.cpp.drl_parser import DRLCPPParser
from biicode.common.edition.processors.parse_processor import ParseProcessor
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.resource import Resource
from mock import Mock
from biicode.common.output_stream import OutputStream
from biicode.common.test.bii_test_case import BiiTestCase


crypto_header = """
namespace CryptoPP {

class CAST
{
protected:
    static const word32 S[8][256];
};
}
"""

crypto_body = """
#include "cryptopp/cryptopp/pch.h"
#include "cryptopp/cryptopp/cast.h"

namespace CryptoPP{

// CAST S-boxes
int CAST::x = 1;
int CAST::y;
int z;

const word32 CAST::S[8][256] = {
{
    0x30FB40D4UL, 0x9FA0FF0BUL, 0x6BECCD2FUL, 0x3F258C7AUL,
    0x1E213F2FUL, 0x9C004DD3UL, 0x6003E540UL, 0xCF9FC949UL,
    0xBFD4AF27UL, 0x88BBBDB5UL, 0xE2034090UL, 0x98D09675UL,
    0x6E63A0E0UL, 0x15C361D2UL, 0xC2E7661DUL, 0x22D4FF8EUL
}}
"""

basic_class_header = '''
class MyClass{
public:
    MyClass();
protected:
    static int a;
};'''
basic_class_body = '''MyClass::MyClass(){}'''
class_static_var_body = '''int MyClass::a = 3;'''
basic_function_header = '''
void myFunction();'''
basic_function_body = '''void myFunction(){}'''
ns_class_header = '''
namespace NS{
class MyClass{
    MyClass();
};
}'''
ns_class_body = '''namespace NS{
MyClass::MyClass(){}
}'''
ns_class_body2 = '''NS::MyClass::MyClass(){}'''
ns_function_header = '''
namespace NS{
void myFunction();
}'''
ns_function_body = '''namespace NS{
void myFunction(){}
}'''
ns_function_body2 = '''
void NS::myFunction(){}
'''

main_body = """
#include "cryptopp/cryptopp/pch.h"
#include "cryptopp/cryptopp/cast.h"

int main(){
return 0;
}
"""
no_main_body = """
#include "cryptopp/cryptopp/pch.h"
#include "cryptopp/cryptopp/cast.h"
"""

poco_header = """#ifndef SAX_LexicalHandler_INCLUDED
#define SAX_LexicalHandler_INCLUDED

#include "Poco/XML/XML.h"
#include "Poco/XML/XMLString.h"

namespace Poco {
namespace XML {


class XML_API LexicalHandler
{
public:
    virtual void startDTD(const XMLString& name) = 0;
    virtual void endDTD() = 0;
    virtual void endCDATA() = 0;
    virtual void comment(const XMLChar ch[], int start, int length) = 0;

protected:
    virtual ~LexicalHandler();
};

} } // namespace Poco::XML

#endif // SAX_LexicalHandler_INCLUDED
"""

poco_src_body = """#include "Poco/SAX/LexicalHandler.h"


namespace Poco {
namespace XML {


LexicalHandler::~LexicalHandler()
{
}


} } // namespace Poco::XML
"""

using_ns_body = """using blobstore::onblocks::utils::ceilDivision;"""

using_ns_header = """namespace blobstore {
namespace onblocks {
namespace utils {

uint32_t intPow(uint32_t base, uint32_t exponent);
uint32_t ceilDivision(uint32_t dividend, uint32_t divisor);
uint32_t maxZeroSubtraction(uint32_t minuend, uint32_t subtrahend);

}
}
}
"""


class CPPImplementationProcessorTest(BiiTestCase):
    '''tests de CPPImplementation processor from 2 sources, from some source files in tests folder
    and from code snippets directly in this file'''

    def _process_from_contents(self, contents):
        '''param contents: dict{name:code snippets}.
        Will create a ProjectHolder, fill with the data and process it'''
        resources = []
        for name, content in contents.iteritems():
            cell = SimpleCell(name, CPP)
            block_name = cell.name.block_name
            resources.append(Resource(cell, Content(name, load=Blob(content),
                                                    parser=DRLCPPParser())))

        block_holder = BlockHolder(block_name, resources)
        self._process(block_holder)
        return block_holder

    def _process_from_files(self, names):
        '''param names: iterable of BlockCellNames. The user will be stripped, and the remaining
        will be loaded from the test folder.
        Will create a ProjectHolder, fill with the data and process it'''
        block_holder = mother.get_block_holder(names, BiiType(CPP))
        self._process(block_holder)
        return block_holder

    def _process(self, block_holder):
        '''helper method that actually invokes the processor'''
        for r in block_holder.simple_resources:
            r.content.parse()
        processor = CPPImplementationsProcessor()
        processor.do_process(block_holder, Mock())

    @parameterized.expand([
        ('user/geom/sphere.h', 'user/geom/sphere.cpp'),
        # find extern implementations of fonts in freeglut
        ('user/glut/src/freeglut_font.c', 'user/glut/src/freeglut_font_data.c'),
        ('user/glut/include/GL/freeglut_std.h', 'user/glut/src/freeglut_glutfont_definitions.c'),
        ('user/gtest/include/gtest/internal/gtest-filepath.h', 'user/gtest/src/gtest-filepath.cc'),
        ('user/solver/systemsolver.h', 'user/solver/systemsolver.cpp'),
        ('user/sdl/include/SDL.h', 'user/sdl/src/SDL.c'),
        ('user/sdl/include/SDL_video.h', 'user/sdl/src/video/SDL_surface.c')

    ])
    def test_implementation_from_files(self, header, source):
        '''basic check that header is implemented by source'''
        sources = [header, source]
        block_holder = self._process_from_files(sources)

        header = BlockCellName(header)
        source = BlockCellName(source)
        header_cell = block_holder[header.cell_name].cell
        self.assertEqual({source}, header_cell.dependencies.implicit)

    def test_find_csparse_implementations(self):
        '''This tests check that the cs.h file requires or is implemented by all other files
        in csparse, (they are all *.c files)'''
        sources = []
        for file_ in testfileutils.get_dir_files('csparse'):
            sources.append('user/csparse/' + file_)

        block_holder = self._process_from_files(sources)

        #Checks
        header = block_holder['cs.h'].cell
        sources = set(sources)
        sources.remove('user/csparse/cs.h')
        self.assertEqual(sources, header.dependencies.implicit)

    @parameterized.expand([
        (crypto_header, crypto_body),
        (basic_class_header, basic_class_body),
        (basic_class_header, class_static_var_body),
        (basic_function_header, basic_function_body),
        (ns_class_header, ns_class_body),
        (ns_class_header, ns_class_body2),
        (ns_function_header, ns_function_body),
        (ns_function_header, ns_function_body2),
        (poco_header, poco_src_body)
    ])
    def test_implementation_from_contents(self, header, source):
        '''basic check that header is implemented by source. The contents of the files are defined
        in snippets of code as strings'''
        sources = {'user/block/header.h': header,
                   'user/block/body.cpp': source}
        block_holder = self._process_from_contents(sources)

        header = BlockCellName('user/block/header.h')
        source = BlockCellName('user/block/body.cpp')
        header_cell = block_holder['header.h'].cell
        self.assertEqual({source}, header_cell.dependencies.implicit)

        #Negative check
        source_cell = block_holder['body.cpp'].cell
        self.assertEqual(set(), source_cell.dependencies.implicit)

    @parameterized.expand([
        ('', ''),
        (crypto_header, ''),
        ('', basic_class_body),
        (using_ns_header, using_ns_body)
    ])
    def test_negative(self, header, source):
        '''some basic negative tests, from snippets of code'''
        sources = {'user/block/header.h': header,
                   'user/block/body.cpp': source}
        block_holder = self._process_from_contents(sources)

        header = BlockCellName('user/block/header.h')
        source = BlockCellName('user/block/body.cpp')
        header_cell = block_holder[header.cell_name].cell
        self.assertEqual(set(), header_cell.dependencies.implicit)

        #Negative check
        source_cell = block_holder[source.cell_name].cell
        self.assertEqual(set(), source_cell.dependencies.implicit)

    def test_has_main(self):
        '''some basic negative tests, from snippets of code'''
        sources = {'user/block/body.cpp': main_body}
        block_holder = self._process_from_contents(sources)

        ParseProcessor().do_process(block_holder, OutputStream())

        self.assertTrue(block_holder._resources['body.cpp'].content.parser.has_main_function())

        sources = {'user/block/body.cpp': no_main_body}
        block_holder = self._process_from_contents(sources)

        ParseProcessor().do_process(block_holder, OutputStream())

        self.assertFalse(block_holder._resources['body.cpp'].content.parser.has_main_function())
