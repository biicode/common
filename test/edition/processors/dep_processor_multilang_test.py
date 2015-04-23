from nose.core import run
from mock import Mock
from biicode.common.model.cells import SimpleCell
from biicode.common.model.bii_type import BiiType, CPP, JS
from biicode.common.edition.processors.dep_processor import DependenciesProcessor
from biicode.common.test.bii_test_case import BiiTestCase
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.model.declare.node_declaration import NodeDeclaration
from biicode.common.model.resource import Resource
from biicode.common.test.edition.processors.helpers import process_holder
from nose.plugins.attrib import attr
from biicode.common.edition.block_holder import BlockHolder
from biicode.common.model.brl.block_name import BlockName


class DependencyProcessorMultilangTest(BiiTestCase):

    @attr('cpp')
    def simple_dependencies_cpp_test(self):
        block_holder = self._cells_setup('dummy/geom', ['sphere.h', 'sphere.cpp', 'main.cpp'], CPP)
        # Parse processor setup

        block_holder['main.cpp'].cell.dependencies.unresolved = {CPPDeclaration('iostream'),
                                                           CPPDeclaration('sphere.h')}
        block_holder['sphere.cpp'].cell.dependencies.unresolved = {CPPDeclaration('math.h'),
                                                                CPPDeclaration('iostream'),
                                                                CPPDeclaration('sphere.h')}
        process_holder(block_holder, DependenciesProcessor())
        # Checks
        mainR = block_holder['main.cpp'].cell
        self.check_dependency_set(mainR.dependencies,
                                   resolved=['sphere.h', 'iostream'],
                                   explicit=['dummy/geom/sphere.h'],
                                   system=['iostream'])

        sphereR = block_holder['sphere.cpp'].cell
        self.check_dependency_set(sphereR.dependencies,
                                   resolved=['sphere.h', 'iostream', 'math.h'],
                                   explicit=['dummy/geom/sphere.h'],
                                   system=['iostream', 'math.h'])

    @attr('node')
    def simple_dependencies_node_test(self):
        block_holder = self._cells_setup('dummy/geom',
                                   ['spherefun.js', 'sphere.js', 'main.js', 'other.js'],
                                   JS)
        # Parse processor setup

        block_holder['main.js'].cell.dependencies.unresolved = {NodeDeclaration('http.js'),
                                                           NodeDeclaration('./sphere.js'),
                                                           NodeDeclaration('other.js')}
        block_holder['sphere.js'].cell.dependencies.unresolved = {NodeDeclaration('http.js'),
                                                             NodeDeclaration('url.js'),
                                                             NodeDeclaration('./spherefun.js')}
        process_holder(block_holder, DependenciesProcessor())

        # Checks
        mainR = block_holder['main.js'].cell
        self.assertEqual(mainR.dependencies.explicit, {'dummy/geom/sphere.js'})
        self.assertEqual(mainR.dependencies.system, {'http.js'})
        self.assertEqual(mainR.dependencies.resolved,
                         {NodeDeclaration('http.js'), NodeDeclaration('./sphere.js')})
        self.assertEqual(mainR.dependencies.unresolved, {NodeDeclaration('other.js')})

        sphereR = block_holder['sphere.js'].cell
        self.assertEqual(sphereR.dependencies.explicit, {'dummy/geom/spherefun.js'})
        self.assertEqual(sphereR.dependencies.system, {'http.js', 'url.js'})
        self.assertEqual(sphereR.dependencies.resolved, {NodeDeclaration('http.js'),
                                                         NodeDeclaration('url.js'),
                                                         NodeDeclaration('./spherefun.js')})
        self.assertEqual(sphereR.dependencies.unresolved, set())

    def _cells_setup(self, block_name, cells_names, biitype):
        resources = []
        block_name = BlockName(block_name)
        for x in cells_names:
            cell = SimpleCell(block_name + x, BiiType(biitype))
            resources.append(Resource(cell, Mock()))
        return BlockHolder(block_name, resources)


if __name__ == 'main':
    run()
