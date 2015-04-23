from nose.core import run
from mock import Mock
from biicode.common.model.cells import SimpleCell, VirtualCell
from biicode.common.model.bii_type import BiiType, CPP
from biicode.common.edition.processors.dep_processor import DependenciesProcessor
from biicode.common.test.bii_test_case import BiiTestCase
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.model.resource import Resource
from biicode.common.model.brl.block_name import BlockName
from biicode.common.test.edition.processors.helpers import process_holder
from biicode.common.edition.block_holder import BlockHolder


class DependencyProcessorTest(BiiTestCase):

    def not_delete_dependant_test(self):
        """ A resolved dependency in the same block must NOT be removed if that exist """
        sphereh = 'dummy/geom/sphere.h'
        block_holder = self._cells_setup('dummy/geom', ['main.cpp', 'sphere.h'], CPP)

        main_cell = block_holder['main.cpp'].cell
        main_cell.dependencies.explicit = {BlockCellName(sphereh)}
        main_cell.dependencies.system = {SystemCellName('iostream')}
        main_cell.dependencies.resolved = {CPPDeclaration('sphere.h'), CPPDeclaration('iostream')}
        process_holder(block_holder, DependenciesProcessor())
        # Checks
        self.check_dependency_set(main_cell.dependencies, resolved=['sphere.h', 'iostream'],
                                   explicit=[sphereh], system=['iostream'])

    def virtual_dependencies_test(self):
        sphereh = 'dummy/geom/sphere.h'
        sphereh_test = 'dummy/geom/test/sphere.h'
        sphereh_dev = 'dummy/geom/develop/sphere.h'

        block_holder = self._cells_setup('dummy/geom', ['main.cpp', 'test/sphere.h', 'main2.cpp',
                                                   'develop/sphere.h'], CPP)
        block_holder._resources['sphere.h'] = Resource(VirtualCell(sphereh), None)
        block_holder['test/sphere.h'].cell.container = BlockCellName(sphereh)
        block_holder['develop/sphere.h'].cell.container = BlockCellName(sphereh)
        block_holder['main.cpp'].cell.dependencies.unresolved = {CPPDeclaration(sphereh_test)}
        block_holder['main2.cpp'].cell.dependencies.unresolved = {CPPDeclaration(sphereh_dev)}
        outputstream = process_holder(block_holder, DependenciesProcessor())
        warn = 'Block dummy/geom has absolute paths, like: #include "dummy/geom/develop/sphere.h"'
        self.assertIn(warn, str(outputstream))

        # Checks
        main_cell = block_holder['main.cpp'].cell
        self.check_dependency_set(main_cell.dependencies, resolved=[sphereh_test],
                                   explicit=[sphereh])
        main_cell = block_holder['main2.cpp'].cell
        self.check_dependency_set(main_cell.dependencies, resolved=[sphereh_dev],
                                   explicit=[sphereh])

    def test_similar_includes(self):
        brls = {'smpso_cpp': 'dummy/jmetal/algorithms/smpso/smpso.cpp',
                'smpso_h': 'dummy/jmetal/algorithms/smpso/smpso.h',
                'pso_settings_cpp': 'dummy/jmetal/settings/pso_settings.cpp',
                'pso_settings_h': 'dummy/jmetal/settings/pso_settings.h',
                'pso_cpp': 'dummy/jmetal/algorithms/pso/pso.cpp',
                'pso_h': 'dummy/jmetal/algorithms/pso/pso.h',
                'pso_main': 'dummy/jmetal/main/pso_main.cpp',
                }
        cells = {x: SimpleCell(x) for x in brls.values()}
        cells_names = [x.name.cell_name for x in cells.itervalues()]
        block_holder = self._cells_setup('dummy/jmetal', cells_names, CPP)

        smpso_cpp = block_holder['algorithms/smpso/smpso.cpp'].cell
        pso_cpp = block_holder['algorithms/pso/pso.cpp'].cell
        pso_settings_h = block_holder['settings/pso_settings.h'].cell
        pso_main = block_holder['main/pso_main.cpp'].cell

        smpso_cpp.dependencies.unresolved = {CPPDeclaration('smpso.h')}
        pso_cpp.dependencies.unresolved = {CPPDeclaration('pso.h')}
        pso_settings_h.dependencies.unresolved = {CPPDeclaration('../algorithms/pso/pso.h')}
        pso_main.dependencies.unresolved = {CPPDeclaration('../algorithms/pso/pso.h')}

        process_holder(block_holder, DependenciesProcessor())
        # Checks
        self.assertEquals(set(), pso_cpp.dependencies.unresolved)
        self.assertEquals(set(), smpso_cpp.dependencies.unresolved)
        self.assertEquals(set(), pso_settings_h.dependencies.unresolved)
        self.assertEquals(set(), pso_main.dependencies.unresolved)

    def test_include_partial(self):
        brls = {'main': 'dummy/block/main.cpp',
                'astar': 'dummy/block/algorithms/astar.h',
                'solver_h': 'dummy/block/solver/solver.h',
                'solver_cpp': 'dummy/block/solver/solver.cpp'
                }
        cells = {x: SimpleCell(x) for x in brls.values()}
        cells_names = [x.name.cell_name for x in cells.itervalues()]
        block_holder = self._cells_setup('dummy/block', cells_names, CPP)

        main = block_holder['main.cpp'].cell
        main.dependencies.unresolved = {CPPDeclaration('solver/solver.h')}
        solver_h = block_holder['solver/solver.h'].cell
        solver_h.dependencies.unresolved = {CPPDeclaration('../algorithms/astar.h')}
        solver_cpp = block_holder['solver/solver.cpp'].cell
        solver_cpp.dependencies.unresolved = {CPPDeclaration('solver.h')}

        process_holder(block_holder, DependenciesProcessor())
        # Checks
        self.assertEquals(set(), cells[brls['main']].dependencies.unresolved)
        self.assertEquals(set(), cells[brls['solver_h']].dependencies.unresolved)
        self.assertEquals(set(), cells[brls['solver_cpp']].dependencies.unresolved)

    def test_duplicated_first_level(self):
        brls = {'gtest1': 'dummy/block/include/gtest/gtest.h',
                'getest2': 'dummy/block/fused-src/gtest/gtest.h',
                'getest-all1': 'dummy/block/fused-src/gtest/gtest-all.cc',
                'getest-all2': 'dummy/block/src/gtest-all.cc',
                'sample': 'dummy/block/samples/sample_unittest.cc'
                }
        cells = {x: SimpleCell(x) for x in brls.values()}
        cells_names = [x.name.cell_name for x in cells.itervalues()]
        block_holder = self._cells_setup('dummy/block', cells_names, CPP)

        getest_all1 = block_holder['fused-src/gtest/gtest-all.cc'].cell
        getest_all1.dependencies.unresolved = {CPPDeclaration('gtest.h')}
        getest_all2 = block_holder['src/gtest-all.cc'].cell
        getest_all2.dependencies.unresolved = {CPPDeclaration('gtest.h')}
        sample = block_holder['samples/sample_unittest.cc'].cell
        sample.dependencies.unresolved = {CPPDeclaration('gtest.h')}
        process_holder(block_holder, DependenciesProcessor())
        # Checks
        self.assertEquals(0, len(getest_all1.dependencies.unresolved))
        self.assertEquals(1, len(getest_all2.dependencies.unresolved))
        self.assertEquals(1, len(sample.dependencies.unresolved))

    def test_duplicated_n_level(self):
        brls = {'gtest1': 'dummy/block/a1/b/c/gtest/gtest.h',
                'getest2': 'dummy/block/a2/gtest/gtest.h',
                'getest-all1': 'dummy/block/a1/gtest-all.cc',
                'getest-all2': 'dummy/block/a3/gtest-all.cc',
                'getest-all3': 'dummy/block/a1/b2/gtest-all.cc',
                }
        cells = {x: SimpleCell(x) for x in brls.values()}
        cells_names = [x.name.cell_name for x in cells.itervalues()]
        block_holder = self._cells_setup('dummy/block', cells_names, CPP)

        getest_all1 = block_holder['a1/gtest-all.cc'].cell
        getest_all1.dependencies.unresolved = {CPPDeclaration('b/c/gtest/gtest.h')}
        getest_all2 = block_holder['a3/gtest-all.cc'].cell
        getest_all2.dependencies.unresolved = {CPPDeclaration('gtest.h')}
        getest_all3 = block_holder['a1/b2/gtest-all.cc'].cell
        getest_all3.dependencies.unresolved = {CPPDeclaration('../b/c/gtest/gtest.h')}
        process_holder(block_holder, DependenciesProcessor())
        # Checks
        self.assertEquals(0, len(getest_all1.dependencies.unresolved))
        self.assertEquals(1, len(getest_all2.dependencies.unresolved))
        self.assertEquals(0, len(getest_all3.dependencies.unresolved))

    @staticmethod
    def _cells_setup(block_name, cells_names, biitype):
        resources = []
        block_name = BlockName(block_name)
        for x in cells_names:
            cell = SimpleCell(block_name + x, BiiType(biitype))
            resources.append(Resource(cell, Mock()))
        return BlockHolder(block_name, resources)

if __name__ == 'main':
    run()
