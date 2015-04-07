import unittest
from biicode.common.edition.parsing.cpp.drl_parser import DRLCPPParser
from biicode.common.model.blob import Blob
from nose_parameterized import parameterized #@UnresolvedImport


class CPPParserTest(unittest.TestCase):
    int_main = """
#include <iostream>

using namespace std;
int main()
{
    cout<<"Hello world"<<endl;
}

"""
    void_main = """
#include <iostream>

using namespace std;
void main()
{
    cout<<"Hello world"<<endl;
}

"""
    params_main = """
#include <iostream>

using namespace std;
int main(int argc, char ** argv) {
    cout<<"Hello world"<<endl;
}

"""
    params_main2 = """
#include <iostream>

int main() {
    cout<<"Hello world"<<endl;
}

"""
    @parameterized.expand([
        (int_main, ),
        (void_main, ),
        (params_main, ),
        (params_main2, )
    ])
    def test_has_main(self, text):
        parser = DRLCPPParser()
        parser.parse(text)
        self.assertTrue(parser.has_main_function())

    def test_scope(self):
        text = """
#include "cryptopp/cryptopp/pch.h"
#include "cryptopp/cryptopp/cast.h"

namespace CryptoPP{

// CAST S-boxes

const word32 CAST::S[8][256] = {
{
    0x30FB40D4UL, 0x9FA0FF0BUL, 0x6BECCD2FUL, 0x3F258C7AUL,
    0x1E213F2FUL, 0x9C004DD3UL, 0x6003E540UL, 0xCF9FC949UL,
    0xBFD4AF27UL, 0x88BBBDB5UL, 0xE2034090UL, 0x98D09675UL,
    0x6E63A0E0UL, 0x15C361D2UL, 0xC2E7661DUL, 0x22D4FF8EUL
}}
"""
        parser = DRLCPPParser()
        parser.parse(text)
        pass
        #self.assertTrue(parser.)
