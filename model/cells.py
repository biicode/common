from biicode.common.model.dependency_set import DependencySet
from biicode.common.utils.serializer import Serializer, Deserializer
from biicode.common.model.brl.block_cell_name import BlockCellName
from biicode.common.model.bii_type import BiiType, UNKNOWN
from biicode.common.model.id import ID
from biicode.common.model.sha import SHABuilder
from biicode.common.exception import BiiSerializationException, ConfigurationFileError
from biicode.common.utils.bii_logging import logger
import traceback


class Cell(object):

    SERIAL_ROOT_KEY = "r"
    SERIAL_ID_KEY = "_id"
    SERIAL_TYPE_KEY = "t"
    SERIAL_NAME_KEY = "n"
    SERIAL_MAIN_KEY = "m"

    def __init__(self, name=None):
        if name and not isinstance(name, BlockCellName):
            name = BlockCellName(name)

        self.name = name
        self.type = BiiType(UNKNOWN)
        '''the root property is intended to be always pointing to a CellID'''
        self.root = None
        '''polimorphic ID, it could be ID published or BlockCellName for Edition'''
        self.ID = name  # By defaults, the ID (edition is the name)
        self.hasMain = False  # FIXME: Probably only in SimpleCell

    def clean_metadata(self):
        self.hasMain = False
        self.root = None
        self.type = BiiType(UNKNOWN)

    def sha(self):
        sh = SHABuilder()
        sh += self.name
        sh += str(self.type)
        sh += str(self.hasMain)
        return sh.sha()

    def __repr__(self):
        return 'Name:%s, Type:%s, Id:%s, Root:%s' % (self.name, self.type, self.ID, self.root)

    def __hash__(self):
        return hash((self.ID, self.name, self.type, self.hasMain, self.root))

    def __eq__(self, other):
        '''The id is not included in the equality, 2 resources with different ID can be equal'''
        if self is other:
            return True
        try:  # root field makes no sense to compare, as in edition it is not assigned
            return  isinstance(other, self.__class__) and \
                    self.name == other.name and \
                    self.type == other.type and \
                    self.hasMain == other.hasMain
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def serialize(self):
        res = Serializer().build(
            (Cell.SERIAL_ROOT_KEY, self.root),  # CellID
            (Cell.SERIAL_ID_KEY, self.ID),  # CellID or BlockCellName
            (Cell.SERIAL_TYPE_KEY, self.type),
            (Cell.SERIAL_NAME_KEY, self.name),
            (Cell.SERIAL_MAIN_KEY, self.hasMain)
        )
        return res


class CellDeserializer(object):
    def __init__(self, id_type):
        '''
        @param id_type BlockCellName or ID
        '''
        self.id_type = id_type

    def deserialize(self, data):
        if data is None:
            return None
        try:
            kls = Deserializer.get_polymorphic_class(data)
            r = kls.deserialize(data)
            r.name = BlockCellName(data[Cell.SERIAL_NAME_KEY])
            r.root = ID.deserialize(data[Cell.SERIAL_ROOT_KEY])
            r.ID = self.id_type.deserialize(data[Cell.SERIAL_ID_KEY])
            r.type = BiiType(data[Cell.SERIAL_TYPE_KEY])
            r.hasMain = data[Cell.SERIAL_MAIN_KEY]
            try:
                r.dependencies.cell_name = r.name
            except AttributeError:
                pass
            return r
        except Exception as e:
            tb = traceback.format_exc()
            logger.warning(tb)
            raise BiiSerializationException(e)


def cell_diff(base, other):
    #TODO: Complete implementation of cell_diff
    if base == other:
        return None
    return 'old %s\nnew %s' % (base, other)


class SimpleCell(Cell):
    """This cell is used for simple or standard resources
    """
    SERIAL_DEPENDENCES_KEY = "d"
    SERIAL_CONTAINER_KEY = "c"
    SERIAL_CONTAINER_TYPE_KEY = "ct"

    def __init__(self, name, biitype=UNKNOWN):
        super(SimpleCell, self).__init__(name)
        self.dependencies = DependencySet()
        self.dependencies.cell_name = self.name
        self.container = None  # CellID or BlockCellName (of the virtual resource)
        self.type = BiiType(biitype)

    def sha(self):
        sh = SHABuilder()
        sh += Cell.sha(self)
        sh += (str(self.dependencies))
        return sh.sha()

    def __repr__(self):
        result = [Cell.__repr__(self)]
        result.append('Dependencies ' + str(self.dependencies))
        result.append('Container ' + str(self.container))
        return '\n'.join(result)

    def serialize(self):
        #res = super(SimpleCell, self).serialize()
        ret = Serializer().build(
                  (None, super(SimpleCell, self)),  # Embed here parent
                  (SimpleCell.SERIAL_DEPENDENCES_KEY, self.dependencies),
                  (SimpleCell.SERIAL_CONTAINER_KEY, self.container),
                  obj=self,
        )
        return ret

    @staticmethod
    def deserialize(data):
        if data is None:
            return None
        r = SimpleCell(None)
        r.dependencies = DependencySet.deserialize(data[SimpleCell.SERIAL_DEPENDENCES_KEY])
        container = data[SimpleCell.SERIAL_CONTAINER_KEY]
        if container:
            r.container = BlockCellName(container)
        return r

    def __eq__(self, other):
        base = Cell.__eq__(self, other)
        return (base and self.dependencies == other.dependencies
                     and self.container == other.container)

    def __ne__(self, other):
        return not self.__eq__(other)

    def clean_metadata(self):
        super(SimpleCell, self).clean_metadata()
        self.dependencies = DependencySet()
        self.container = None


class VirtualCell(Cell):
    """This cell is used with virtual resources
    """
    SERIAL_CODETREE_KEY = "f"
    SERIAL_LEAVES_KEY = "l"

    def __init__(self, name, code=None, leaves=None):
        super(VirtualCell, self).__init__(name)
        self.code = code or ""
        self.leaves = leaves or set()

    @property
    def resource_leaves(self):
        tokens = self.name.rsplit('/', 1)
        return [BlockCellName('%s/%s/%s' % (tokens[0], name, tokens[1])) for name in self.leaves]

    def __str__(self):
        result = [Cell.__str__(self)]
        result.append('Code %s' % self.code)
        return '\n'.join(result)

    def __repr__(self):
        result = [Cell.__repr__(self)]
        result.append('Leaves %s' % self.leaves)
        return '\n'.join(result)

    def evaluate(self, settings):
        aux = {}
        exec self.code in aux
        f = aux['virtual']
        tokens = self.name.rsplit('/', 1)
        try:
            evaluated = f(settings)
            return BlockCellName('%s/%s/%s' % (tokens[0], evaluated, tokens[1]))
        except Exception as e:
            raise ConfigurationFileError("Error evaluating virtual resource %s, %s. "
                                         "Check virtual.bii and try again" % (self.ID, e))

    def serialize(self):
        return  Serializer().build(
                    (None, super(VirtualCell, self)),  # Embed here parent
                    (VirtualCell.SERIAL_CODETREE_KEY, self.code),
                    (VirtualCell.SERIAL_LEAVES_KEY, self.leaves),
                    obj=self,
                )

    @staticmethod
    def deserialize(data):
        r = VirtualCell(None)
        r.code = data[VirtualCell.SERIAL_CODETREE_KEY]
        if data[VirtualCell.SERIAL_LEAVES_KEY] is None:
            r.leaves = set()
        else:
            r.leaves = set(data[VirtualCell.SERIAL_LEAVES_KEY])
        return r

    def __eq__(self, other):
        base = Cell.__eq__(self, other)
        return (base and self.leaves == other.leaves
                     and self.code == other.code)

    def __ne__(self, other):
        return not self.__eq__(other)
