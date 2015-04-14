import unittest
from biicode.common.edition.parsing.code_reference import CodeReference


class CodeReferenceTest(unittest.TestCase):

    def testEquals(self):
        coderef = CodeReference("name", 10, 20)
        coderef2 = CodeReference("name", 10, 21)
        coderef3 = CodeReference("name", 10, 20)
        self.assertEqual(coderef, coderef)
        self.assertNotEqual(coderef, "asdasd")
        self.assertNotEqual(coderef, coderef2)
        self.assertEqual(coderef, coderef3)
