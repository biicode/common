import unittest
from nose_parameterized import parameterized
from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.symbolic.reference import Reference, ReferencedResources, References
from biicode.common.deps.closure import Closure, ClosureItem
from biicode.common.model.resource import Resource
from biicode.common.model.cells import SimpleCell, VirtualCell
from biicode.common.settings.settings import Settings
from biicode.common.settings.osinfo import OSInfo, OSFamily
from biicode.common.deps.block_version_graph import BlockVersionGraph
from biicode.common.model.bii_type import CPP
from biicode.common.deps.closure_builder import build_closure
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.output_stream import OutputStream


va = BlockVersion(BRLBlock('user/user/blocka/master'), 4)
vb = BlockVersion(BRLBlock('user/user/blockb/branch'), 2)
vb2 = BlockVersion(BRLBlock('user/user/blockb/branch'), 3)
vd1 = BlockVersion(BRLBlock('user/user/blockd/branch'), 5)
vd2 = BlockVersion(BRLBlock('user/user/blockd/branch'), 3)
vc = BlockVersion(BRLBlock('user/user/blockc/branch'), None)


class FakeApi():
    def __init__(self, resources, tables):
        """ Input: {version: resource}
        """
        self._resources = {}  # {Reference: Resource}
        for version, resource in resources:
            self._resources[Reference(version, resource.cell_name)] = resource
        self._tables = {}
        for version, dep_versions in tables.iteritems():
            self._tables[version] = BlockVersionTable(dep_versions)

    def get_published_resources(self, references):
        result = ReferencedResources()
        for ref in references.explode():
            result[ref.block_version][ref.ref] = self._resources[ref]
        return result

    def get_cells_snapshot(self, block_version):
        return []

    def get_dep_table(self, block_version):
        return self._tables[block_version]


class ClosureBuildingTest(unittest.TestCase):

    def simple_test(self):
        """ Blocks: C
        Deps: A, B
        C -> A -> B
        """
        references = References()
        references[va].add('a.h')
        base_table = BlockVersionTable([vc, va])  # The result including or excluding va is same

        b = Resource(SimpleCell('user/blockb/b.h'))
        a = Resource(SimpleCell('user/blocka/a.h'))
        a2 = Resource(SimpleCell('user/blocka/a2.h'))
        a.cell.dependencies.explicit.add(a2.name)
        a2.cell.dependencies.explicit.add(b.name)

        tables = {va: [vb], vb: []}
        api = FakeApi(zip([va, va, vb], [a, a2, b]), tables)
        biiout = OutputStream()
        graph, closure, _ = build_closure(api, references, base_table, biiout=biiout)
        expected_graph = BlockVersionGraph()
        expected_graph.add_nodes([va, vb])
        expected_graph.add_edge(va, vb)
        self.assertEqual(expected_graph, graph)
        expected_closure = Closure({a.name: ClosureItem(a, va),
                                    a2.name: ClosureItem(a2, va),
                                    b.name: ClosureItem(b, vb)})
        self.assertEqual(expected_closure, closure)
        self.assertEqual("", str(biiout))

    def overwrite_test(self):
        """ Blocks: C (defines in requirements B2)
        Deps: A, B2
        C -> A -> B1
        """
        references = References()
        references[va].add('a.h')

        b = Resource(SimpleCell('user/blockb/b.h'))
        b2 = Resource(SimpleCell('user/blockb/b.h'), CPP)
        a = Resource(SimpleCell('user/blocka/a.h'))
        a2 = Resource(SimpleCell('user/blocka/a2.h'))
        a.cell.dependencies.explicit.add(a2.name)
        a2.cell.dependencies.explicit.add(b.name)

        tables = {va: [vb], vb: [], vb2: []}
        api = FakeApi(zip([va, va, vb, vb2], [a, a2, b, b2]), tables)
        base_table = BlockVersionTable([vc, va, vb2])  # Note B2 defined here
        biiout = OutputStream()
        graph, closure, _ = build_closure(api, references, base_table, biiout=biiout)
        expected_graph = BlockVersionGraph()
        expected_graph.add_nodes([va, vb2])
        expected_graph.add_edge(va, vb2)
        self.assertEqual(expected_graph, graph)
        expected_closure = Closure({a.name: ClosureItem(a, va),
                                    a2.name: ClosureItem(a2, va),
                                    b.name: ClosureItem(b2, vb2)})
        self.assertEqual(expected_closure, closure)
        self.assertEqual("", str(biiout))

    def dep_overwriten_in_blocks_test(self):
        """ Blocks: C, B (None version)
        Deps: A
        C -> A -> B
        """
        references = References()
        references[va].add('a.h')
        vbn = BlockVersion(vb.block, None)

        b = Resource(SimpleCell('user/blockb/b.h'))
        a = Resource(SimpleCell('user/blocka/a.h'))
        a2 = Resource(SimpleCell('user/blocka/a2.h'))
        a.cell.dependencies.explicit.add(a2.name)
        a2.cell.dependencies.explicit.add(b.name)

        tables = {va: [vb], vb: []}
        api = FakeApi(zip([va, va, vb], [a, a2, b]), tables)
        base_table = BlockVersionTable([vc, vbn])
        biiout = OutputStream()
        graph, closure, _ = build_closure(api, references, base_table, biiout=biiout)
        expected_graph = BlockVersionGraph()
        expected_graph.add_nodes([va])
        expected_graph.add_edge(va, vbn)
        self.assertEqual(expected_graph, graph)
        expected_closure = Closure({a.name: ClosureItem(a, va),
                                    a2.name: ClosureItem(a2, va)})
        self.assertEqual(expected_closure, closure)
        self.assertEqual("", str(biiout))

    @parameterized.expand([
        (True,),
        (False, ),
    ])
    def diamond_test(self, conflict):
        """ Blocks: C
        Deps: A, B, D1-D2
        C -> A, B; A->D1, B->D2
        """
        references = References()
        references[va].add('a.h')
        references[vb].add('b.h')

        b = Resource(SimpleCell('user/blockb/b.h'))
        a = Resource(SimpleCell('user/blocka/a.h'))
        d1 = Resource(SimpleCell('user/blockd/d.h'))
        if conflict:
            d2 = Resource(SimpleCell('user/blockd/d.h', CPP))
        else:
            d2 = Resource(SimpleCell('user/blockd/d.h'))
        a.cell.dependencies.explicit.add(d1.name)
        b.cell.dependencies.explicit.add(d2.name)

        tables = {va: [vd1], vb: [vd2], vd1: [], vd2: []}
        api = FakeApi(zip([va, vb, vd1, vd2], [a, b, d1, d2]), tables)
        base_table = BlockVersionTable([vc, va, vb])
        biiout = OutputStream()
        graph, closure, _ = build_closure(api, references, base_table, biiout=biiout)
        expected_graph = BlockVersionGraph()
        expected_graph.add_nodes([va, vb, vd1, vd2])
        expected_graph.add_edge(va, vd1)
        expected_graph.add_edge(vb, vd2)
        self.assertEqual(expected_graph, graph)
        self.assertEqual({a.name, b.name, d1.name}, set(closure.keys()))
        if conflict:
            self.assertIn('Incompatible dependency "user/blockd/d.h"', str(biiout))
        else:
            self.assertEqual("", str(biiout))

    def virtual_test(self):
        references = References()
        references[va].add('a.h')

        code = ('def virtual(settings):\n\tif(settings.os.family == "windows"):return "win"\n'
                '\telse: return "nix"')
        a = Resource(VirtualCell('user/blocka/a.h', code, {'win', 'nix'}))

        awin = Resource(SimpleCell('user/blocka/win/a.h'))
        anix = Resource(SimpleCell('user/blocka/nix/a.h'))
        b = Resource(SimpleCell('user/blockb/b.h'))
        d1 = Resource(SimpleCell('user/blockd/d.h'))
        awin.cell.dependencies.explicit.add(b.name)
        anix.cell.dependencies.explicit.add(d1.name)

        tables = {va: [vb, vd1], vb: [], vd1: []}
        api = FakeApi(zip([va, va, va, vb, vd1], [a, awin, anix, b, d1]), tables)

        #With windows settings
        settings = Settings(OSInfo(OSFamily("Windows")))
        biiout = OutputStream()
        graph, closure, _ = build_closure(api, references, {}, settings, biiout)
        expected_graph = BlockVersionGraph()
        expected_graph.add_nodes([va, vb])
        expected_graph.add_edge(va, vb)
        self.assertEqual(expected_graph, graph)
        expected_closure = Closure({a.name: ClosureItem(a, va),
                                    awin.name: ClosureItem(awin, va),
                                    b.name: ClosureItem(b, vb),
                                    })
        self.assertEqual(expected_closure, closure)
        self.assertEqual("", str(biiout))

        #Change settings
        settings = Settings(OSInfo(OSFamily("Linux")))
        biiout = OutputStream()
        graph, closure, _ = build_closure(api, references, {}, settings, biiout)
        expected_graph = BlockVersionGraph()
        expected_graph.add_nodes([va, vd1])
        expected_graph.add_edge(va, vd1)
        self.assertEqual(expected_graph, graph)
        expected_closure = Closure({a.name: ClosureItem(a, va),
                                    anix.name: ClosureItem(anix, va),
                                    d1.name: ClosureItem(d1, vd1),
                                    })
        self.assertEqual(expected_closure, closure)
        self.assertEqual("", str(biiout))
