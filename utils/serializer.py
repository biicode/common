from biicode.common.exception import BiiSerializationException


class ClassTypedSerializer(object):

    __typed_classes = None

    @staticmethod
    def import_typed_classes():
        '''Workaround for avoid cyclic import problem'''
        if ClassTypedSerializer.__typed_classes is None:
            from biicode.common.model.cells import VirtualCell, SimpleCell
            from biicode.common.model.declare.python_declaration import PythonDeclaration
            from biicode.common.model.declare.cpp_declaration import CPPDeclaration
            from biicode.common.model.declare.node_declaration import NodeDeclaration
            from biicode.common.model.declare.data_declaration import DataDeclaration
            from biicode.common.model.declare.java_declaration import JavaDeclaration
            from biicode.common.model.declare.fortran_declaration import FortranDeclaration
            from biicode.common.model.declare.cmake_declaration import CMakeDeclaration

            ClassTypedSerializer.__typed_classes = {  # DO NOT CHANGE THIS ENUM VALUES EVER!!!
                         SimpleCell: 0,
                         VirtualCell: 1,
                         DataDeclaration: 2,
                         CPPDeclaration: 3,
                         PythonDeclaration: 4,
                         NodeDeclaration: 5,
                         JavaDeclaration: 6,
                         FortranDeclaration: 7,
                         CMakeDeclaration: 8
            }

            ClassTypedSerializer.__typed_classes_reverse = {  # DO NOT CHANGE THIS VALUES EVER!!!
                         0: SimpleCell,
                         1: VirtualCell,
                         2: DataDeclaration,
                         3: CPPDeclaration,
                         4: PythonDeclaration,
                         5: NodeDeclaration,
                         6: JavaDeclaration,
                         7: FortranDeclaration,
                         8: CMakeDeclaration
            }

    @staticmethod
    def getClass(value):
        ClassTypedSerializer.import_typed_classes()
        return ClassTypedSerializer.__typed_classes_reverse[value]

    @staticmethod
    def getValue(obj_kls):
        ClassTypedSerializer.import_typed_classes()
        ret = None
        try:
            ret = ClassTypedSerializer.__typed_classes[obj_kls]
            return ret
        except KeyError:
            return None


class SetDeserializer(object):

    def __init__(self, kls):
        self.kls = kls

    def deserialize(self, elements):
        if elements is None:
            return None
        if callable(getattr(self.kls, "deserialize", None)):
            return set(self.kls.deserialize(elem) for elem in elements)
        else:
            return set(self.kls(elem) for elem in elements)


class ListDeserializer(object):

    def __init__(self, kls):
        self.kls = kls

    def deserialize(self, elements):
        if callable(getattr(self.kls, "deserialize", None)):
            return [self.kls.deserialize(elem) for elem in elements]
        else:
            return [self.kls(elem) for elem in elements]


class DictDeserializer(object):

    def __init__(self, kls_key=None, kls_value=None):
        self.kls_key = kls_key
        self.kls_value = kls_value

    def deserialize(self, elements):
        if elements is None:
            return None
        ret = {}
        #Dict or tuple like Serialize.build_dict does. (k,v),(k,v) for mongo
        if isinstance(elements, dict):
            elements = elements.iteritems()
        key_has_deserialize = callable(getattr(self.kls_key, "deserialize", None))
        val_has_deserialize = callable(getattr(self.kls_value, "deserialize", None))
        for k, v in elements:
            if self.kls_key is not None:
                key_obj = self.kls_key.deserialize(k) if key_has_deserialize else self.kls_key(k)
            else:
                key_obj = k
            if self.kls_value is not None:
                val_obj = None if v is None else self.kls_value.deserialize(v) \
                          if val_has_deserialize else self.kls_value(v)
            else:
                val_obj = v
            ret[key_obj] = val_obj
        return ret


class Deserializer(object):

    POLIMORPHIC_KEYWORD = "_k"

    @staticmethod
    def get_polymorphic_class(data):
        try:
            kls = ClassTypedSerializer.getClass(data[Deserializer.POLIMORPHIC_KEYWORD])
        except KeyError:
            raise BiiSerializationException("Cant deserialize object without know his class!! " \
                                            + str(data))
        return kls


def serialize(value):
    serializer = getattr(value, 'serialize', None)
    if serializer:
        return serializer()
    elif isinstance(value, (tuple, list, set)):
        return [serialize(item) for item in value]
    elif isinstance(value, dict):
        return [(serialize(k), serialize(v)) for k, v in value.iteritems()]
    else:
        return value


class Serializer(object):
    """Build recursive object calling METHOD_RECURSIVE.
       Expects list with (key,value) elements (not dictionaries).
       If key is None the subelement is embedded in parent

    """

    def build(self, *args, **kwargs):
        '''Builds a hash'''
        ret = {}
        if "obj" in kwargs:
            self.assign_class_type(ret, kwargs["obj"], Deserializer.POLIMORPHIC_KEYWORD)

        for arg in args:
            key = arg[0]
            value = arg[1]
            value = serialize(value)
            if key is None:
                self.append_values(ret, value)
            else:
                self.append_values(ret, {key: value})
        return ret

    def assign_class_type(self, ret, obj, key=Deserializer.POLIMORPHIC_KEYWORD):
        '''For serialized class names'''
        if obj is None:
            return ret
        # print "OBJETO TIPADO!!"
        if not isinstance(obj, type):
            obj = obj.__class__
        tp = ClassTypedSerializer.getValue(obj)
        #print "DE CLASE: " + str(obj.__class__)+" ->"+str(tp)+" ->"+str(obj)
        if tp is None:
            raise BiiSerializationException("Add class for %s" % str(obj))

        self.append_values(ret, {key: tp})

    def append_values(self, ret, values):
        len_ret = len(ret)
        ret.update(values)
        len_final = len(ret)
        if len_final != len_ret + len(values):
            raise ValueError("Duplicated key")
