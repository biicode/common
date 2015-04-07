from biicode.common.model.symbolic.block_version_table import BlockVersionTable
from biicode.common.exception import NotFoundException


class DepsApiFake(object):
    def __init__(self, table_dict):
        self.tables = {}
        for version, versions in table_dict.iteritems():
            self.tables[version] = BlockVersionTable(versions)

    def get_dep_table(self, version):
        try:
            return self.tables[version]
        except:
            raise NotFoundException()
