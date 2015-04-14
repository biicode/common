import unittest
from biicode.common.edition.processors.deps_conf_file import (DependentConfiguration,
                                                              DependencyConfiguration,
                                                              parse_deps_conf)
from biicode.common.exception import ConfigurationFileError


class DependenciesConfigurationFileParserTest(unittest.TestCase):

    def test_parses_empty_file(self):
        deps = parse_deps_conf("", 0)
        self.assertEquals(deps, [])

    def test_parses_wrong_file(self):
        with self.assertRaisesRegexp(ConfigurationFileError, "2: Parse error"):
            parse_deps_conf("\n28\n", 0)

    def test_parses_file_with_negated_dependencies(self):
        text = r'''file.h + NULL'''
        deps = parse_deps_conf(text, 0)
        self.assertEquals(deps[0].pattern, 'file.h')
        self.assertEquals(deps[0].action, DependentConfiguration.ADD_FLAG)
        self.assertEquals(deps[0].dependencies, set())
        self.assertEquals(len(deps), 1)

    def test_parses_file_with_negated_dependencies_and_rubbish(self):
        text = r'''file.h + NULL i dont mind'''
        deps = parse_deps_conf(text, 0)
        self.assertEquals(deps[0], DependentConfiguration('file.h', '+', set()))
        self.assertEquals(len(deps), 1)

    def test_parses_file_with_negated_and_dependencies(self):
        text = r'''
        file.h - NULL i dont mind
        math.h = test.cpp name.h'''
        deps = parse_deps_conf(text, 0)
        self.assertEquals(deps[0], DependentConfiguration('file.h', '-', set()))
        self.assertEquals(deps[1], DependentConfiguration('math.h', '=',
                                {DependencyConfiguration(False, 'test.cpp'),
                                 DependencyConfiguration(False, 'name.h')}))
        self.assertEquals(len(deps), 2)

    def test_parses_file_with_list_depencendies(self):
        text = '''
        r1.h + !r2.cpp r3.cpp'''
        deps = parse_deps_conf(text, 0)
        self.assertEquals(deps[0], DependentConfiguration('r1.h', '+',
                                 {DependencyConfiguration(True, 'r2.cpp'),
                                 DependencyConfiguration(False, 'r3.cpp')}))
        self.assertEquals(len(deps), 1)
