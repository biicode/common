import unittest
from biicode.common.model.server_info import ServerInfo, ClientVersion


class ServerInfoTest(unittest.TestCase):
    def test_invalid_msg(self):
        server_info = ServerInfo(message=u'\xa0')
        self.assertNotEquals(server_info.messages, '\xa0')

    def test_serialize(self):
        sut = ServerInfo()
        sut.download_url = 'https://www.biicode.com/downloads'
        serial = sut.serialize()
        deserialized = ServerInfo.deserialize(serial)
        self.assertEquals(sut, deserialized)


class ClientVersionTest(unittest.TestCase):
    def test_compare(self):
        self.assertEqual(ClientVersion('develop'), ClientVersion('develop'))
        self.assertFalse(ClientVersion('1.2') > ClientVersion('develop'))
        self.assertGreater(ClientVersion('develop'), ClientVersion('1.2'))
        self.assertLess(ClientVersion('1.2'), ClientVersion('develop'))
        self.assertGreater(ClientVersion('1.3'), ClientVersion('1.2'))
        self.assertLess(ClientVersion('1.2'), ClientVersion('1.3'))
        self.assertGreater(ClientVersion('1.3.5'), ClientVersion('1.3'))
        self.assertLess(ClientVersion('1.3'), ClientVersion('1.3.5'))
        self.assertFalse(ClientVersion('0.1.13.2') > ClientVersion('0.2'))
        self.assertFalse(ClientVersion('0.2') < ClientVersion('0.1.13.2'))
