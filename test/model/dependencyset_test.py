import unittest
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.dependency_set import DependencySet
from biicode.common.model.declare.cpp_declaration import CPPDeclaration


class DependendencySetTest(unittest.TestCase):
    def update_test(self):
        deps = DependencySet()
        brl1 = BlockCellName("user/module/mytest.h")
        dec = CPPDeclaration("name1")
        deps.unresolved.add(brl1)
        deps.explicit.add(brl1)
        deps.resolved.add(dec)

        deps2 = DependencySet()
        brl2 = BlockCellName("user/module/mytest2.h")
        dec2 = CPPDeclaration("name2")
        deps2.unresolved.add(brl2)
        deps2.explicit.add(brl2)
        deps2.resolved.add(dec2)

        deps.update(deps2)
        self.assertIn(brl1, deps.unresolved)
        self.assertIn(brl1, deps.explicit)
        self.assertIn(dec, deps.resolved)
        self.assertIn(brl2, deps.unresolved)
        self.assertIn(brl2, deps.explicit)
        self.assertIn(dec2, deps.resolved)
