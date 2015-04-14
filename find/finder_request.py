from biicode.common.utils.serializer import Serializer, SetDeserializer
from biicode.common.model.brl.block_name import BlockName
from biicode.common.find.policy import Policy
from biicode.common.model.symbolic.reference import ReferencedDependencies
from collections import defaultdict
from biicode.common.utils.bii_logging import logger
from biicode.common.model.declare.declaration import Declaration
from biicode.common.model.symbolic.block_version_table import BlockVersionTable


class FinderRequest(object):

    def __init__(self, policy=None):
        self.unresolved = set()  # Unresolved declarations to be found
        self.block_names = set()  # Current hive src blocks, to forbid cycles
        self.existing = ReferencedDependencies()  # Current resolved deps
        self.existing_common_table = BlockVersionTable()
        self.policy = policy
        self.find = True  # To find for UNRESOLVED
        self.update = False  # To activate UPDATES
        self.downgrade = False  # To activate DOWNGRADES
        self.modify = False  # Allow changing deps to non-descendant branches

    def __len__(self):
        l = 0
        if self.find:
            l += len(self.unresolved)
        if self.modify or self.update or self.downgrade:
            l += len(self.existing)
        return l

    def possible_blocks(self):
        '''
        Returns: { block_name: set(Declaration) }
        '''
        possible_blocks = defaultdict(set)
        for declaration in self.unresolved:
            try:
                block = declaration.block()
                if block and block not in self.block_names:
                    # FIXME: If block is in self.block_names the client could had filter that
                    possible_blocks[block].add(declaration)
            except Exception as e:
                logger.debug('Could not obtain block from decl %s: %s' % (declaration, str(e)))
        return possible_blocks

    def __repr__(self):
        result = []
        result.append('Unresolved: ' + str(self.unresolved))
        result.append('Existing: ' + str(self.existing))
        result.append('CurrentBlocks: ' + str(self.block_names))
        return '\n'.join(result)

    SERIAL_UNRESOLVED_KEY = "u"
    SERIAL_TRACKING_KEY = "t"
    SERIAL_EXISTING_KEY = "e"
    SERIAL_POLICY = "p"
    SERIAL_CRITERIA = 'c'
    SERIAL_DEP_COMMON_TABLE = 'd'

    @staticmethod
    def deserialize(data):
        '''From dictionary to object FinderRequest'''
        ret = FinderRequest()
        ret.block_names = SetDeserializer(BlockName).deserialize(data[FinderRequest.SERIAL_TRACKING_KEY])
        ret.existing = ReferencedDependencies.deserialize(data[FinderRequest.SERIAL_EXISTING_KEY])
        ret.unresolved = SetDeserializer(Declaration).deserialize(data[FinderRequest.SERIAL_UNRESOLVED_KEY])
        ret.policy = Policy.deserialize(data[FinderRequest.SERIAL_POLICY])
        criteria = data[FinderRequest.SERIAL_CRITERIA]
        ret.find, ret.update, ret.downgrade, ret.modify = criteria
        ret.existing_common_table = BlockVersionTable.deserialize(data[FinderRequest.SERIAL_DEP_COMMON_TABLE])
        return ret

    def serialize(self):
        return Serializer().build((FinderRequest.SERIAL_UNRESOLVED_KEY, self.unresolved),
                                  (FinderRequest.SERIAL_TRACKING_KEY, self.block_names),
                                  (FinderRequest.SERIAL_EXISTING_KEY, self.existing),
                                  (FinderRequest.SERIAL_POLICY, self.policy),
                                  (FinderRequest.SERIAL_DEP_COMMON_TABLE, self.existing_common_table),
                                  (FinderRequest.SERIAL_CRITERIA, (self.find,
                                                                   self.update,
                                                                   self.downgrade,
                                                                   self.modify)))

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) \
            and other.unresolved == self.unresolved \
            and other.block_names == self.block_names \
            and other.existing == self.existing \
            and other.policy == self.policy \
            and other.find == self.find \
            and other.update == self.update \
            and other.downgrade == self.downgrade \
            and other.modify == self.modify \
            and other.existing_common_table == self.existing_common_table

    def __ne__(self, other):
        return not self.__eq__(other)
