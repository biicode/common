import unittest
from biicode.common.model.brl.cell_name import CellName


class CellNameTest(unittest.TestCase):

    def test_name(self):
        self.assertEqual("Path/To/File.h", CellName("Path/To\File.h"))
        self.assertEqual("Path/To2/File2.h", CellName("Path/To2/File2.h"))
        self.assertEqual("File2.h", CellName("File2.h"))
        self.assertEqual("File-INternal.H", CellName("File-INternal.H"))
        self.assertEqual("Path/To/CamelCase.Java", CellName("Path\To/CamelCase.Java"))
        self.assertEqual("Path/To/under_score.py", CellName("Path/To/under_score.py"))
        self.assertEqual("CamelCase.Java", CellName("CamelCase.Java"))

        CellName("m#")
        CellName("$var")
        CellName("m&")
        CellName("var()")
        CellName("Path/To/CamelCase&.Java")
        CellName("Path/To&/CamelCase.Java")

    def test_extensions(self):
        self.assertEqual(".h", CellName("Path/To/File.h").extension)
        self.assertEqual(".cpp", CellName("Path/To/File.CPP").extension)
        self.assertEqual("", CellName("Path/To/File").extension)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
