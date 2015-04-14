import unittest
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.find.policy import Policy
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.version_tag import ALPHA, STABLE, DEV, BETA
from biicode.common.exception import BiiException


policy_yaml = '''
# This is one comment
diego/geom2(branch1): ALPHA
diego/geom: BETA
diego2/geom3(*): DEV
diego2/geom4(pepe/*): STABLE
john/*: DEV
'''


class PolicyTest(unittest.TestCase):

    def test_serialize_policy(self):
        p = Policy.loads(policy_yaml)
        self.assertEqual(p[0].tag, ALPHA)
        self.assertEqual(p[0].block, "diego/geom2(branch1)")
        self.assertEqual(p[1].tag, BETA)
        self.assertEqual(p[1].block, "diego/geom")
        d = p.serialize()
        p2 = Policy.deserialize(d)
        self.assertEqual(p, p2)

    def test_errors(self):
        with self.assertRaisesRegexp(BiiException, "Incorrect rule in policies.bii"):
            Policy.loads("*: ALFA")
        with self.assertRaisesRegexp(BiiException, "Incorrect rule in policies.bii"):
            Policy.loads("what")
        with self.assertRaisesRegexp(BiiException, "Empty policies.bii, cannot find"):
            Policy.loads("#adasd\n#asdasd\n")

    def test_evaluate(self):
        p = Policy.loads(policy_yaml)
        m = BlockVersion(BRLBlock('diego/diego/geom/master'), 3)
        self.assertEqual(False, p.evaluate(m, DEV))
        self.assertEqual(False, p.evaluate(m, ALPHA))
        self.assertEqual(True, p.evaluate(m, BETA))
        self.assertEqual(True, p.evaluate(m, STABLE))
        m = BlockVersion(BRLBlock('diego/diego/geom2/branch1'), 4)
        self.assertEqual(True, p.evaluate(m, ALPHA))
        self.assertEqual(False, p.evaluate(m, DEV))
        self.assertEqual(True, p.evaluate(m, BETA))
        self.assertEqual(True, p.evaluate(m, STABLE))
        m = BlockVersion(BRLBlock('diego2/diego2/geom3/branch1'), 4)
        self.assertEqual(True, p.evaluate(m, ALPHA))
        self.assertEqual(True, p.evaluate(m, DEV))
        self.assertEqual(True, p.evaluate(m, BETA))
        self.assertEqual(True, p.evaluate(m, STABLE))
        m = BlockVersion(BRLBlock('anyuser/diego2/geom3/anybranch'), 4)
        self.assertEqual(True, p.evaluate(m, ALPHA))
        self.assertEqual(True, p.evaluate(m, DEV))
        self.assertEqual(True, p.evaluate(m, BETA))
        self.assertEqual(True, p.evaluate(m, STABLE))
        m = BlockVersion(BRLBlock('anyuser/diego2/geom4/anybranch'), 4)
        self.assertEqual(False, p.evaluate(m, ALPHA))
        self.assertEqual(False, p.evaluate(m, DEV))
        self.assertEqual(False, p.evaluate(m, BETA))
        self.assertEqual(False, p.evaluate(m, STABLE))
        m = BlockVersion(BRLBlock('pepe/diego2/geom4/anybranch'), 4)
        self.assertEqual(False, p.evaluate(m, ALPHA))
        self.assertEqual(False, p.evaluate(m, DEV))
        self.assertEqual(False, p.evaluate(m, BETA))
        self.assertEqual(True, p.evaluate(m, STABLE))
        m = BlockVersion(BRLBlock('pepe/john/geom4/anybranch'), 4)
        self.assertEqual(True, p.evaluate(m, ALPHA))
        self.assertEqual(True, p.evaluate(m, DEV))
        self.assertEqual(True, p.evaluate(m, BETA))
        self.assertEqual(True, p.evaluate(m, STABLE))

        p = Policy.loads("*: DEV")
        m = BlockVersion(BRLBlock('diego/diego/geom/master'), 3)
        self.assertEqual(True, p.evaluate(m, DEV))
        self.assertEqual(True, p.evaluate(m, ALPHA))
        self.assertEqual(True, p.evaluate(m, BETA))
        self.assertEqual(True, p.evaluate(m, STABLE))
