from biicode.common.exception import BiiException

__author__ = 'victor'

import unittest
from biicode.common.model.brl.brl_user import BRLUser


class BRLUserTest(unittest.TestCase):
    def test_simple_name(self):

        _ = BRLUser("testuser1")
        _ = BRLUser(" testuser2 ")
        _ = BRLUser(" TestUser3 ")
        _ = BRLUser("abdmvn___s")
        _ = BRLUser("  ficherito_33")
        self.assertRaises(BiiException, BRLUser, "2testuser")
        self.assertRaises(BiiException, BRLUser, "_testuser")
        self.assertRaises(BiiException, BRLUser, "22")
        self.assertRaises(BiiException, BRLUser, "m")
        self.assertRaises(BiiException, BRLUser, "m" * 51)
        self.assertRaises(BiiException, BRLUser, "")
        self.assertRaises(BiiException, BRLUser, "=jkllf89o")
        self.assertRaises(BiiException, BRLUser, "hola-adios")
        self.assertRaises(BiiException, BRLUser, "TheSimpsons!!!")
        self.assertRaises(BiiException, BRLUser, "aaaaa*aaaaaa")
        self.assertRaises(BiiException, BRLUser, "'; delete from users")
        self.assertRaises(BiiException, BRLUser, "\"; delete from users")
        self.assertRaises(BiiException, BRLUser, "  33_ficherito ")

