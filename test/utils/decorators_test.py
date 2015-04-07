import unittest
from mock import Mock, patch
from mock import call
from biicode.common.utils.decorators import os_constraint
from biicode.common.settings.osinfo import OSInfo


class DecoratorsTest(unittest.TestCase):

    @patch('biicode.common.utils.decorators.OSInfo')
    def test_constraint_os_same_os(self, os_info):
        class Aux(object):

            def __init__(self, os_name_mock):
                os_info.capture = Mock(return_value=OSInfo(os_name_mock))
                self.user_io = Mock()

            @os_constraint("Linux")
            def linux_call(self):
                self.linux = 1

            @os_constraint("Windows")
            def windows_call(self):
                self.windows = 2

        aux_instance = Aux("Linux")
        aux_instance.linux_call()
        aux_instance.windows_call()
        self.assertEquals(aux_instance.linux, 1)
        aux_instance.user_io.assert_has_calls([call.out.error('You need to use a Windows OS')])

        aux_instance = Aux("Windows")
        aux_instance.linux_call()
        aux_instance.windows_call()
        self.assertEquals(aux_instance.windows, 2)
        aux_instance.user_io.assert_has_calls([call.out.error('You need to use a Linux OS')])
