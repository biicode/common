import unittest
from biicode.common.settings.tools import Builder, Compiler, Runner


class BuilderTest(unittest.TestCase):
    def builder_serialization_test(self):
        tool = Builder()
        serial = tool.serialize()
        deserial = Builder.deserialize(serial)
        self.assertEquals(tool, deserial)


class CompilerTest(unittest.TestCase):
    def compiler_serialization_test(self):
        tool = Compiler()
        serial = tool.serialize()
        deserial = Compiler.deserialize(serial)
        self.assertEquals(tool, deserial)


class RunnerTest(unittest.TestCase):
    def runner_serialization_test(self):
        tool = Runner()
        serial = tool.serialize()
        deserial = Runner.deserialize(serial)
        self.assertEquals(tool, deserial)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
