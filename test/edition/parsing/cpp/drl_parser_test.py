import unittest
from biicode.common.edition.parsing.cpp.drl_parser import DRLCPPParser
from biicode.common.edition.parsing.code_reference import CPPItem
from biicode.common.test import testfileutils
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.model.declare.data_declaration import DataDeclaration
from biicode.common.edition.parsing.file_parser import FileParser


example = r'''// prueba.cpp:
//

#include "stdafx.h" //Another comment

#include <iostream> //One comment

#define MYVALUE 3 //example define

int a;
float b = 0.0f;

extern double c;
float suma(float a, float b) //comment
{
    //suma
    return a+b;
}
class PreDecl //My predc
    ;
float multiply(float a, float b);
class
Sphere : public Shape//MyClass comment
{
protected:
    float radius;
public:
    Sphere(float r):radius(r){ /*Inline coment*/};
    float volume(){
        return radius*radius*radius;
    }
    float methodDecl();
};

namespace Geom
{
    float intersect();
    float other(){
        return 0.0f;
    }
    class Line{

    };
}
float Geom::intersect(){
    return 0;
}
/* Multiline comment
asdasd

asd*/
using namespace std;
int main()
{
    Sphere s(2.0f);
    cout<<"Volume: "<<s.volume()<<endl;
    cout<<suma(2,3)<<endl;
    cout<<Geom::intersect()<<endl;
    return 1;
}'''


class DRLCPPParserTest(unittest.TestCase):

    def test_destructor(self):
        text = r"""
namespace Poco {
LexicalHandler::~LexicalHandler()
{
}
}"""
        parser = DRLCPPParser()
        parser.parse(text)
        self.assertEqual(CPPItem(CPPItem.METHOD, '~LexicalHandler', 'Poco::LexicalHandler'),
                         parser.definitions.pop())

    def test_includes(self):
        testIncludes = r'''
//comment
#include <iostream>
#include "file.h"
//#include "path/to/file2.h"
/*#include "file3.h" /**/*/
# include    "path/to/file4.h "
#include " file5.h " //Comment on include
#include <file6.h > /*Other comment*/
#define MYVAR 3
'''
        parser = DRLCPPParser()
        parser.parse(testIncludes)

        obtained = [ref.name for ref in parser.includes]
        expected = ['iostream', 'file.h', 'path/to/file4.h',
                      'file5.h', 'file6.h']
        self.assertEqual(expected, obtained)

    def test_declaration_defintions(self):
        text = r'''
int a;
float b = 0.0f;

extern double c;
float suma(float a, float b) //comment
{
    //suma
    return a+b;
}
class PreDecl //My predc
    ;
float multiply(float a, float b);
class
    Sphere : public Polygon//MyClass comment
{
protected:
    float radius;
public:
    Sphere(float r):radius(r){ /*Inline coment*/};
    float volume(){
        return radius*radius*radius;
    }
    float methodDecl();
};
'''
        parser = DRLCPPParser()
        parser.parse(text)

        expected = set([CPPItem(CPPItem.CLASS, 'Sphere'),
                        CPPItem(CPPItem.VAR, 'c'),
                        CPPItem(CPPItem.METHOD, 'multiply'),
                        ])

        #print parser.declarations
        self.assertEqual(expected, parser.declarations)

        expected = set([CPPItem(CPPItem.VAR, 'a'),
                        CPPItem(CPPItem.VAR, 'b'),
                        CPPItem(CPPItem.METHOD, 'suma'),
                        ])

        self.assertEqual(expected, parser.definitions)

    def test_namespace(self):
        text = r'''
namespace Geom
{
    float intersect();
    float other(){
        return 0.0f;
    }
    class Line{

    };
    namespace NS{
        float foo();
        class Bar{
        };
    }
}
float Geom::intersect(){
    return 0;
}
float Geom::NS::intersect2(){
    return 0;
}
'''
        parser = DRLCPPParser()
        parser.parse(text)

        expected = set([CPPItem(CPPItem.CLASS, 'Line', 'Geom'),
                        CPPItem(CPPItem.METHOD, 'intersect', 'Geom'),
                        CPPItem(CPPItem.CLASS, 'Bar', 'Geom::NS'),
                        CPPItem(CPPItem.METHOD, 'foo', 'Geom::NS'),
                        ])

        self.assertEqual(expected, parser.declarations)

        expected = set([CPPItem(CPPItem.METHOD, 'other',  'Geom'),
                        CPPItem(CPPItem.METHOD, 'intersect', 'Geom'),
                        CPPItem(CPPItem.METHOD, 'intersect2', 'Geom::NS'),
                        ])

        self.assertEqual(expected, parser.definitions)

    def test_explicit_dependencies(self):
        text = r'''
/*
 * Prueba de comentario en clase
 */
class Sphere
{
protected:
    float radius;
        protectedMethod();
        protectedMethod2(MYSTRUCT m);
public:
        ///Contructor
    Sphere(float r);
    ///bii://user/module/file
    float volume();

    ///bii://user2/module2/file2
    double hhh(){
                return 2*2;
    }
};'''
        parser = DRLCPPParser()
        parser.parse(text)
        explicitDependencies = parser.explicit_declarations
        expected = set(['user/module/file', 'user2/module2/file2'])
        self.assertSetEqual(expected,
                            set([str(expDep) for expDep in explicitDependencies]))

    def test_parse_escaped_strings(self):
        text = r'''
string a = "Hello \"world\""
string b = "Hello \"world\"\\"
int c = 8;
'''
        file_parser = FileParser()
        result, _ = file_parser._parse_strings_comments(text)
        self.assertEqual(r'"Hello \"world\""', result[0].content)
        self.assertEqual(r'"Hello \"world\"\\"', result[1].content)

    def test_parse_escaped_strings2(self):
        text = r'''cout << "   \"" << (char *)testSet[i].input << '\"';'''
        file_parser = FileParser()
        result, _ = file_parser._parse_strings_comments(text)
        self.assertEqual(r'"   \""', result[0].content)
        self.assertEqual(r"'\"'", result[1].content)

    def test_replace_includes(self):
        text = r'''# include   "file.h" //My comment
 # include   "file2.h"
# include   "path/to/file.h" //My comment
# include   "file3.h"
//bii://biicode.txt
'''
        parser = DRLCPPParser()
        parser.parse(text)
        d1 = CPPDeclaration('file.h')
        d2 = CPPDeclaration('user/block/file.h')
        text = parser.updateDeclaration(text, d1, d2)

        d1 = CPPDeclaration('file3.h')
        d2 = CPPDeclaration('user/block2/file3.h')
        text = parser.updateDeclaration(text, d1, d2)

        d1 = CPPDeclaration('file2.h')
        d2 = CPPDeclaration('user/block2/file2.h')
        text = parser.updateDeclaration(text, d1, d2)

        d1 = DataDeclaration('biicode.txt')
        d2 = DataDeclaration('user/block/biicode.txt')
        text = parser.updateDeclaration(text, d1, d2)
        expected = '''# include   "user/block/file.h" //My comment
 # include   "user/block2/file2.h"
# include   "path/to/file.h" //My comment
# include   "user/block2/file3.h"
//bii://user/block/biicode.txt
'''
        self.assertEqual(expected, text)

    def test_find_gtest_implementations(self):
        text = testfileutils.load('gtest/src/gtest-death-test.cc')
        parser = DRLCPPParser()
        parser.parse(text)
        self.assertIn(CPPDeclaration('../include/gtest/internal/gtest-port.h'),
                      parser.explicit_declarations)

    def test_scope_in_const_definition(self):
        code = """
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
        parser = DRLCPPParser()
        parser.parse(code)
        expected = set([CPPItem(type_=CPPItem.VAR, name='S', scope='CryptoPP::CAST'),
                        CPPItem(type_=CPPItem.VAR, name='x', scope='CryptoPP::CAST'),
                        CPPItem(type_=CPPItem.VAR, name='y', scope='CryptoPP::CAST'),
                        CPPItem(type_=CPPItem.VAR, name='z', scope='CryptoPP')])
        self.assertItemsEqual(expected, parser.definitions)

    def test_arduino_imports(self):
        arduino_imports = """#import "hola.h"
#include "fran/duino/fancy.h"

void setup(){
    foo();
}

void loop(){
    bar();
}
"""
        parser = DRLCPPParser()
        parser.parse(arduino_imports)
        obtained_includes = [ref.name for ref in parser.includes]
        expected = ['hola.h', 'fran/duino/fancy.h']
        self.assertItemsEqual(expected, obtained_includes)
