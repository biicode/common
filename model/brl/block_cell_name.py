from biicode.common.model.brl.cell_name import CellName
from biicode.common.model.brl.block_name import BlockName
from biicode.common.exception import InvalidNameException


class BlockCellName(str):
    '''block/cell
       [user/block]/cell
    '''
    def __new__(cls, value, validate=True):
        if not validate:
            obj = str.__new__(cls, value)
        else:
            try:
                value = value.strip().replace('\\', '/')
                tokens = value.split('/', 2)
                cell = CellName(tokens[2])
                block = BlockName('/'.join(tokens[:2]))
                obj = str.__new__(cls, '%s/%s' % (block, cell))
                obj._block = block
                obj._cell = cell
            except IndexError:
                error_message = 'Invalid BlockCellName %s. '\
                                'It should be in the form usr/block/cellname' % value
                raise InvalidNameException(error_message)
        return obj

    def _parse(self):
        # Data must be already validated
        tokens = self.split('/', 2)
        self._block = BlockName('/'.join(tokens[:2]), False)
        self._cell = CellName(tokens[2], False)

    @property
    def user_name(self):
        return self.block_name.user

    @property
    def block_name(self):
        try:
            return self._block
        except:
            self._parse()
            return self._block

    @property
    def cell_name(self):
        try:
            return self._cell
        except:
            self._parse()
            return self._cell

    @property
    def extension(self):
        return self.cell_name.extension

    def serialize(self):
        return self[:]

    @staticmethod
    def deserialize(data):
        return BlockCellName(data, False)
