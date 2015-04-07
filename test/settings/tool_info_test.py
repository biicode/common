import unittest
from biicode.common.settings.tool_info import ToolInfo


class ToolInfoTest(unittest.TestCase):

    def tool_info_serialization_test(self):
        tool = ToolInfo()
        serial = tool.serialize()
        deserial = ToolInfo.deserialize(serial)
        self.assertEquals(tool, deserial)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()