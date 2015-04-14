
from biicode.common.utils.serializer import Serializer, ListDeserializer
from biicode.common.model.brl.system_cell_name import SystemCellName
from biicode.common.dev.system_id import SystemID
from bson import BSON
from biicode.common.utils import file_utils


class SystemResourceNames(object):

    SERIAL_ID_KEY = "sr_id"
    SERIAL_NAMES_KEY = "names"

    def __init__(self, system_id):
        self.system_id = system_id
        self._names = []  # of SystemCellName

    @property
    def names(self):
        return self._names

    def add_names(self, names):
        '''to ensure all elements are indeed SystemCellName'''
        for name in names:
            self._names.append(SystemCellName(name))

    @staticmethod
    def read_file(path):
        serial = file_utils.load(path)
        serial = BSON(serial)
        serial = BSON.decode(serial)
        srn = SystemResourceNames.deserialize(serial)
        return srn

    def serialize(self):
        ret = Serializer().build(
              (SystemResourceNames.SERIAL_ID_KEY, self.system_id),
              (SystemResourceNames.SERIAL_NAMES_KEY, self._names)
              )
        return ret

    @staticmethod
    def deserialize(data):
        '''From dictionary to object '''
        sr_id = SystemID.deserialize(data[SystemResourceNames.SERIAL_ID_KEY])
        ret = SystemResourceNames(sr_id)
        ldeserializer = ListDeserializer(SystemCellName)
        ret._names = ldeserializer.deserialize(data[SystemResourceNames.SERIAL_NAMES_KEY])
        return ret

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, self.__class__):
            return self.system_id == other.system_id and \
                   self._names == other._names
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
