from unittest import TestCase
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.model.brl.block_cell_name import BlockCellName
import copy
import tempfile
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.test.conf import BII_TEST_FOLDER
from biicode.common.utils.bii_logging import logger
import re


class BiiTestCase(TestCase):
    '''Base test class with custom assertions'''
    _multiprocess_shared_ = True

    @staticmethod
    def new_tmp_folder():
        folder = tempfile.mkdtemp(suffix='biicode', dir=BII_TEST_FOLDER)
        logger.debug('Temp folder: %s' % folder)
        return folder

    def check_dependency_set(self, dependencies, explicit=None, implicit=None, data=None,
                              system=None, resolved=None, unresolved=None,
                              declaration=CPPDeclaration):
        '''custom assertion to check DependencySet
        system is a list of strings ['iostream', 'math.h']
        resolved is a iterable of strings 'user/module/file.h, 'iostream.h'.
        If None, will be computed from system+explicit
        unresolved is similar to resolved, but names can be shorter, as are not resolved
        unresolved {'sphere.h': Type:EXCPLICIT_CODE}'''

        system = system or set()
        explicit = explicit or set()
        implicit = implicit or set()
        data = data or set()
        unresolved = unresolved or set()
        if not resolved:
            resolved = set(copy.copy(system))
            resolved.update(explicit)

        systemDeps = set([SystemCellName(s) for s in system])
        self.assertEqual(systemDeps, dependencies.system,
                         'System dependencies do not match.\n\tExpected: %s\n\tObtained: %s' \
                         % (systemDeps, dependencies.system))

        explicitDeps = set([BlockCellName(s) for s in explicit])
        self.assertEqual(explicitDeps, dependencies.explicit,
                         'Explicit dependencies do not match.\n\tExpected: %s\n\tObtained: %s' \
                         % (explicitDeps, dependencies.explicit))

        dataDeps = set([BlockCellName(s) for s in data])
        self.assertEqual(dataDeps, dependencies.data,
                         'Data dependencies do not match.\n\tExpected: %s\n\tObtained: %s' \
                         % (dataDeps, dependencies.data))

        implicitDeps = set([BlockCellName(s) for s in implicit])
        self.assertEqual(implicitDeps, dependencies.implicit,
                         'Implicit dependencies do not match.\n\tExpected: %s\n\tObtained: %s' \
                         % (implicitDeps, dependencies.implicit))

        unresolvedDeps = set([declaration(name) for name in unresolved])
        self.assertEqual(unresolvedDeps, dependencies.unresolved,
                         'Unresolved dependencies do not match.\n\tExpected: %s\n\tObtained: %s' \
                         % (unresolvedDeps, dependencies.unresolved))

        resolvedDeps = set([declaration(name) for name in resolved])
        self.assertEqual(resolvedDeps, dependencies.resolved,
                         'Resolved dependencies do not match.\n\tExpected %s\n\tObtained: %s' \
                         % (resolvedDeps, dependencies.resolved))

    def assert_in_response(self, response, message):
        self.assertIn(message, str(response))

    def assert_not_in_response(self, response, message):
        self.assertNotIn(message, str(response))

    def assert_in_output(self, messages, output):
        '''check that the messages are in the output string
        if messages is iterable (not string), it checks that all items are found in the same
        order. If messages is a string it must be found.
        Output is converted to string and normalized CRLF so messages to found are always LF only
        '''
        output = str(output)  # Just in case output is BiiResponse
        output = output.replace('\x1b[?1034h', '')  # Bright red in mac, does not match ANSI regexp
        ansi_escape = re.compile(r'\x1b[^m]*m')
        output = ansi_escape.sub('', output)  # replaces all matches of the regexp in data with ''
        output = output.replace(b'\r\n', '\n')  # Normalize windows output
        if isinstance(messages, basestring):
            self.assertIn(messages, output)
        else:
            for message in messages:
                message = message.strip()  # Do not take into account whitespaces
                index = output.find(message)
                if index == -1:
                    raise AssertionError('"%s" not in \n %s' % (message, output))
                output = output[index + 1:]

    def assert_not_in_ouput(self, messages, output):
        self.assertRaises(AssertionError, self.assert_in_output, messages, output)

    def assert_published(self, output, block_version):
        '''Params:
            output: command output
            block_version: BlockVersion
        '''
        msg = "Successfully published %s" % str(block_version)
        self.assert_in_output(msg, output)
        #self.assert_in_output("You can find your block at", output)

    def assert_bii_equal(self, obj1, obj2):
        """ Convenience method to check two entities are exactly the same,
        for example after a serialization-deserialization cycle
        It is recursive, goes down the contained sub-objects
        """

        if isinstance(obj1, (list, tuple, set)):  # assume iterables
            for v1, v2 in zip(obj1, obj2):
                self.assert_bii_equal(v1, v2)
        elif isinstance(obj1, (basestring, int, bool)):  # string based
            self.assertEqual(obj1, obj2)
        else:
            self.assertEqual(dir(obj1), dir(obj2))
            for key, value in obj1.__dict__.iteritems():
                try:
                    self.assert_bii_equal(value, obj2.__dict__[key])
                except AttributeError:  # No __dict__
                    self.assertEqual(value, obj2.__dict__[key])
