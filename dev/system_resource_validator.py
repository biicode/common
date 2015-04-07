from biicode.common.model.bii_type import UNKNOWN
import os
from biicode.common.dev import DEV_DIR
from biicode.common.utils import file_utils
from collections import defaultdict
from biicode.common.dev.system_resource_names import SystemResourceNames


def getSystemNameValidatorFor(cell):
    return Validators.get_validator(cell.type)


class Validators(object):
    _sr_ids = {}  # static dict for Sr_Ids srID : key
    _instances = {}

    @staticmethod
    def get_validator(biitype):
        if biitype in Validators._instances:
            return Validators._instances[biitype]

        srv = SystemResourceValidator(biitype)
        # Note: IMPORTANT this lower, to convert CPP to dir "cpp"
        srv.add_dir(repr(biitype).lower())
        Validators._instances[biitype] = srv
        return srv

    @staticmethod
    def get_index(sr):
        try:
            return Validators._sr_ids[sr]
        except:
            n = len(Validators._sr_ids)
            Validators._sr_ids[sr] = n
            return n


class SystemResourceValidator(object):

    def __init__(self, biitype=UNKNOWN):
        self.biitype = biitype
        self._map = defaultdict(list)

    def add(self, srn):
        if self.biitype == UNKNOWN:
            self.biitype = srn.system_id.biiType
        if self.biitype == srn.system_id.biiType:
            index = Validators.get_index(srn.system_id)
            for res in srn.names:
                self._map[res].append(index)

    def add_dir(self, _path):
        path = file_utils.resource_path(DEV_DIR, os.path.join('devsys', _path))
        if not os.path.exists(path):
            return
        for f in os.listdir(path):
            srn = SystemResourceNames.read_file(os.path.join(path, f))
            self.add(srn)

    def names(self):
        '''returns a set of SystemCellNames for this type'''
        return self._map.keys()
