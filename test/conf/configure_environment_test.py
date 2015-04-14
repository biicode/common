import unittest
from biicode.common.conf.configure_environment import get_env, default_type
from nose_parameterized import parameterized


env = {'MR_POTATO': 'head',
       'i': 'a,b,c',
       'J': '12',
       'k': 'True',
       'L': 'False',
       'm': '1',
       'N': '0',
       'P': None}


class ConfEnvironmentTest(unittest.TestCase):

    @parameterized.expand(
        [('def', 'A', 'def'),
         (['a'], 'B', ['a']),
         (1, 'C', 1),
         (True, 'D', True),
         (False, 'E', False),
         (True, 'F', True),
         (True, 'G', True),
         (None, 'H', None),
         (['a'], 'i', ['a', 'b', 'c']),
         (1, 'J', 12),
         (True, 'k', False),
         (True, 'L', False),
         (False, 'm', True),
         (True, 'N', False),
         (None, 'P', None),
         ('a', 'MR_POTATO', 'head')
         ])
    def simple_test(self, default_value, env_key, result):
        self.assertEqual(get_env(env_key, default_value, env), result)

    @parameterized.expand(
        [(['a'], 'a,b,c', ['a', 'b', 'c']),
         ('a', 'aaa', 'aaa'),
         (1, '12', 12),
         (True, '0', False),
         (True, 'False', False),
         (True, '1', True),
         (True, 'True', False),
         (None, None, None)])
    def type_function_test(self, default_value, env_value, result):
        func = default_type[type(default_value)]
        self.assertEqual(func(env_value), result)
