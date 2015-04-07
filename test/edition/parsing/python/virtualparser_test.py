import unittest
from biicode.common.edition.parsing.virtual.virtualparser import parseFile, VirtualParseResult

testOK = '''
def func(settings):
    """sphere.h, sphere.cpp"""
    if(settings.osInfo.is_windows()):
        return "win"
    else:
        return "nix"

def func2(settings):
    """cube.h"""
    if(settings.osInfo.isLinux()):
        return "linux"
    else:
        return "default"
'''

testOKM1 = '''def virtual(settings):
    """sphere.h, sphere.cpp"""
    if(settings.osInfo.is_windows()):
        return "win"
    else:
        return "nix"'''

testOKM2 = '''def virtual(settings):
    """cube.h"""
    if(settings.osInfo.isLinux()):
        return "linux"
    else:
        return "default"'''


class VirtualParserTest(unittest.TestCase):
    '''Testing parsing of virtual configuration files '''

    def testCorrectParsing(self):
        p = parseFile(testOK)
        self.assertEqual(set(['sphere.cpp', 'sphere.h']), p['func'].apply)
        self.assertEqual(set(['win', 'nix']), p['func'].leaves)
        self.assertEqual(testOKM1, p['func'].code)

        self.assertEqual(set(['cube.h']), p['func2'].apply)
        self.assertEqual(set(['linux', 'default']), p['func2'].leaves)
        self.assertEqual(testOKM2, p['func2'].code)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
