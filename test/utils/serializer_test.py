import unittest
from biicode.common.utils.serializer import Serializer, DictDeserializer
from biicode.common.model.brl.block_cell_name import BlockCellName


class DummyA(object):

    a = None
    b = None

    def __init__(self, *args, **kwargs):
        self.a = 1
        self.b = 2

    def serialize(self):
        return  Serializer().build(("a", self.a), ("b", self.b))


class DummyB(DummyA):

    def __init__(self, *args, **kwargs):
        self.a = DummyA()
        self.b = 2

    def serialize(self):
        return  Serializer().build(("a", self.a), ("b", self.b))


class DummyC(DummyB):

    def serialize(self):
        return  Serializer().build(("a", self.a), ("b", self.b))


class DummyD(object):

    def serialize(self):
        return  Serializer().build(("list", ("uno", "dos")))


class DummyE(DummyB):

    def serialize(self):
        return  Serializer().build(("list", (self.a, "dos")))

    def __init__(self, *args, **kwargs):
        self.a = DummyA()
        self.b = 2


class SerializerTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__a = DummyA()
        self.__b = DummyB()
        self.__c = DummyC()
        self.__d = DummyD()
        self.__e = DummyE()

    def testKeyRepeated(self):
        ''' should raise an exception for a repeated key '''
        self.assertRaises(ValueError,
                          Serializer().build,
                          ("k2", "value2"), ("k", "value3"), ("k2", "value4")
                          )

    def testRecursiveSerialization(self):
        ''' should call to_dict from DummyA '''
        s = Serializer().build(
                              ("a", self.__a),
                              ("b", 122)
                             )
        self.assertEqual(s, {"a": {"a": 1, "b": 2}, "b": 122})

    def testRecursiveSerialization2(self):
        ''' should call to_dict from DummyA and DummyB '''
        s = Serializer().build(
                              ("a", self.__a),
                              ("b", self.__b)
                             )
        self.assertEqual(s, {"a": {"a": 1, "b": 2}, "b": {"a": {"a": 1, "b": 2}, "b": 2}})

    def testKeyRepeatedEmbedding(self):
        self.assertRaises(ValueError,
                           Serializer().build,
                              (None, self.__a),  # Embed DummyA here, "b" key repeated
                              ("b", self.__b)
                             )

    def testEmbed(self):
        s = Serializer().build(
                          (None, self.__a),
                          ("c", self.__c)
                        )
        self.assertEqual(s, {'a': 1, 'b': 2, 'c': {'a': {'a': 1, 'b': 2}, 'b': 2}})

    def testObjectWithList(self):
        s = Serializer().build(
                          (None, self.__a),
                          ("d", self.__d)
                        )
        self.assertEqual(s, {'a': 1, 'b': 2, 'd': {'list': ["uno", "dos"]}})

    def testObjectWithComplexList(self):
        s = Serializer().build(
                          (None, self.__a),
                          ("e", self.__e)
                        )
        self.assertEqual(s, {'a': 1, 'b': 2, 'e': {'list': [{'a': 1, 'b': 2}, "dos"]}})


class TestDictDeserializer(unittest.TestCase):

    def test_deserialize_none(self):
        dd = DictDeserializer(str, str)
        self.assertIsNone(dd.deserialize(None))

    def testDeserializeDict(self):
        brl = BlockCellName("user/block/path/file.h")
        brl2 = BlockCellName("user/block/path/file2.h")

        h = {brl.serialize(): "asasdasdasd",
             brl2.serialize(): "1123"
        }
        ret = DictDeserializer(BlockCellName, str).deserialize(h)
        self.assertEqual(ret, {'user/block/path/file.h': 'asasdasdasd',
                               'user/block/path/file2.h': '1123'})

        h = {brl.serialize(): brl.serialize(),
             brl2.serialize(): brl.serialize()
        }

        ret = DictDeserializer(BlockCellName, BlockCellName).deserialize(h)
        self.assertEqual(ret,
                         {'user/block/path/file.h': 'user/block/path/file.h',
                          'user/block/path/file2.h': 'user/block/path/file.h'}
                        )
