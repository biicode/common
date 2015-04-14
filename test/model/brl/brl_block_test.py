import unittest
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.brl.brl_user import BRLUser
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.symbolic.block_version import BlockVersion
import json
from biicode.common.exception import InvalidNameException
from biicode.common.model.brl.complex_name import ComplexName


class BRLBlockTest(unittest.TestCase):

    def testParsing(self):
        brl = BRLBlock("drodri/pedro/geom/mybranch")
        self.assertEqual(BRLUser('drodri'), brl.owner)
        self.assertEqual('drodri', brl.owner)
        self.assertEqual('pedro/geom', brl.block_name)
        self.assertEqual(BlockName('pedro/geom'), brl.block_name)
        self.assertEqual(ComplexName('mybranch'), brl.branch)
        self.assertEqual('mybranch', brl.branch)

    def testLowerCaseBackslashConversion(self):
        brl = BRLBlock("Drodri\Pedro/geOm\Mybranch")
        self.assertEqual(BRLUser('Drodri'), brl.owner)
        self.assertEqual('Drodri', brl.owner)
        self.assertEqual('Pedro/geOm', brl.block_name)
        self.assertEqual(BlockName('Pedro/geOm'), brl.block_name)
        self.assertEqual(ComplexName('mybranch'), brl.branch)
        self.assertEqual('mybranch', brl.branch)

    def test_pretty(self):
        brl = BRLBlock("drodri/pedro/geOm/mybranch")
        self.assertEqual('pedro/geOm(drodri/mybranch)', brl.to_pretty())

    def testJson(self):
        brl = BRLBlock("drodri/pedro/geom/mybranch")
        js = json.dumps(brl)
        brl2 = json.loads(js)
        self.assertEqual(brl, brl2)

    def testAdd(self):
        brl = BRLBlock("drodri/user/geom/mybranch")
        v = brl + 3
        self.assertEqual(BlockVersion(brl, 3), v)

    def testisBranched(self):
        brl = BRLBlock("drodri/user/geom/mybranch")
        self.assertTrue(brl.is_branched)

    def testAddCellName(self):
        brl = BRLBlock("drodri/user/geom/mybranch")
        block_cell_name = brl + "test.cpp"
        self.assertEquals(BlockCellName("user/geom/test.cpp"), block_cell_name)

    def test_invalid_names(self):
        #All valid, not raises
        brl = BRLBlock("validowner/validcreator/va__-lidblocknam.e/validbranch")
        self.assertEqual(brl.block_name.name, "va__-lidblocknam.e")

        #All valid, not raises
        brl = BRLBlock("validowner/validcreator/v123/validbranch")
        self.assertEqual(brl.block_name.name, "v123")

        #Invalid block
        self.assertRaises(InvalidNameException,
                          BRLBlock,
                          "inva.lid.owner/validcreator/v/validbranch")

        #Invalid owner
        self.assertRaises(InvalidNameException,
                          BRLBlock,
                          "inva.lid.owner/validcreator/va__-lidblocknam.e/validbranch")
        #Invalid creator
        with self.assertRaises(InvalidNameException) as cm:
            BRLBlock("validowner/.vali-dcreator/va__-lidb.e/validbranch")

        self.assertIn("Valid names should begin with alphanumerical characters",
                       cm.exception.message)

        #Invalid branch
        with self.assertRaises(InvalidNameException) as cm:
            BRLBlock("validowner/validcreator/va__-lidb.e/.invalidbranch")

        self.assertIn("Valid names MUST begin with a letter or number",
                       cm.exception.message)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
