from biicode.common.utils.serializer import DictDeserializer
from biicode.common.model.brl.cell_name import CellName
from biicode.common.utils.bii_logging import logger


class Renames(dict):
    '''renames is a dict {CellName: CellName} where the key is the old name
    and the value is the new name'''

    def cat(self, rename):
        '''compose two renames, in-place '''
        for old_name, new_name in rename.items():
            self[self.get_old_name(old_name)] = new_name

    def get_old_name(self, new_name):
        '''get key by value, or return value if not found'''
        for old, new in self.iteritems():
            if new == new_name:
                return old
        return new_name

    def __setitem__(self, old_name, new_name):
        assert isinstance(old_name, CellName)
        assert isinstance(new_name, CellName)
        if old_name == new_name:
            logger.error('Rename with the same name %s' % old_name)
            return
        super(Renames, self).__setitem__(old_name, new_name)

    @staticmethod
    def deserialize(data):
        return Renames(DictDeserializer(CellName, CellName).deserialize(data))
