import unittest
from biicode.common.edition.parsing.file_parser import FileParser
from biicode.common.edition.parsing.code_reference import CPPItem


class FileParserTest(unittest.TestCase):

    def test_multiline_define(self):
        text = r'''#if !defined(_WIN32) && !defined(WIN32) && !defined(_WRS_KERNEL) \
 && !defined(__minux)
void kk(int a);
# else
void pun(int a);
 # endif'''

        parser = FileParser()
        includes, refs, declarations, definitions, comments = parser.parse(text)
        self.assertIn(CPPItem(CPPItem.METHOD, 'pun', ''), declarations)
        self.assertIn(CPPItem(CPPItem.METHOD, 'kk', ''), declarations)

    def test_escape_single_character(self):
        text = r"""int a=3;
        char b='\'';
        char c='c';
        char d='\'';
        char e='e';
        int main(){
        }
        """
        parser = FileParser()
        includes, refs, declarations, definitions, comments = parser.parse(text)
        #print parser.declarations
        #print parser.definitions
        self.assertIn(CPPItem(CPPItem.METHOD, 'main', ''), definitions)
        self.assertIn(CPPItem(CPPItem.VAR, 'a', ''), definitions)
        self.assertIn(CPPItem(CPPItem.VAR, 'b', ''), definitions)
        self.assertIn(CPPItem(CPPItem.VAR, 'c', ''), definitions)
        self.assertIn(CPPItem(CPPItem.VAR, 'd', ''), definitions)
        self.assertIn(CPPItem(CPPItem.VAR, 'e', ''), definitions)
