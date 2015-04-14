from biicode.common.utils.serializer import Serializer, Deserializer, SetDeserializer
from abc import ABCMeta, abstractmethod
from biicode.common.model.deps_props import DependenciesProperties


class Declaration(object):
    __metaclass__ = ABCMeta
    SERIAL_DATA_KEY = 'd'
    SERIAL_EXCLUDE_KEY = 'ex'
    SERIAL_PROPERTIES = 'p'

    def __init__(self, name):
        """ The name of the dependency, initially what the user types "include/cube.h",
        "com.biicode.Class" or "from mypackage.foo import bar".
        The Case is stored as typed by the user, no changes until found and managed by biicode
        """
        self.name = name
        self.properties = set()

    def __lt__(self, other):
        # required for printing alphabetically ordered list of declarations
        return self.name.lower() < other.name.lower()

    @abstractmethod
    def match(self, block_cell_names, origin_block_cell_name=None, paths=None):
        """
        Params:
            @block_cell_names: iterable of BlockCellName that can be used to resolve declaration
            @origin_block_cell_name: the BlockCellName of the Resource that declares
                                     this declaration
        Return: set of BlockCellName, empty if no match or a subset of block_cell_names if
                successfully match
        There are dependencies that require more than one file per declaration
        (i.e.: packages, or initialicers of modules). Cpp is always one-to-one,
        but python could be one-to-many
        """
        raise NotImplementedError("Please implement this method")

    @abstractmethod
    def block(self):
        """The matching BlockName can be extracted without targets info, it is always absolute
          (#include "user/test/file.h", import user.test.File, from user.test import File)
          @return: matching BlockName, None if not possible to deduce block
        """
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def normalize(self, target_block_cell_names):
        '''@return: None if no change is necessary, or a new XXXDeclaration that matches targets'''
        raise NotImplementedError("Please Implement this method")

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def serialize(self):
        return Serializer().build(
                            (Declaration.SERIAL_DATA_KEY, self.name),
                            (Declaration.SERIAL_PROPERTIES, self.properties),
                            obj=self
                )

    @staticmethod
    def deserialize(data):
        kls = Deserializer.get_polymorphic_class(data)
        obj = kls(data[Declaration.SERIAL_DATA_KEY])
        try:
            d = data[Declaration.SERIAL_PROPERTIES]
            props = SetDeserializer(str).deserialize(d)
            obj.properties = props
        except KeyError:
            pass
        try:
            d = data[Declaration.SERIAL_EXCLUDE_KEY]
            if d:
                obj.properties.add(DependenciesProperties.EXCLUDE_FROM_BUILD)
        except KeyError:
            pass
        return obj
