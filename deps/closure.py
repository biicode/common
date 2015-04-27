from collections import namedtuple
from biicode.common.edition.block_holder import BIICODE_FILE
from biicode.common.exception import ConfigurationFileError
from biicode.common.edition.bii_config import BiiConfig


ClosureItem = namedtuple('ClosureItem', 'resource version')


class Closure(dict):
    '''A connected set of resources {BlockCellName: (Resource, Version)}'''

    def add_item(self, resource, version, biiout):
        old_item = self.get(resource.name)
        #assert old_item.version != version if old_item else True, "Adding the same resource!"
        if old_item and old_item.resource != resource:
            biiout.error('Incompatible dependency "%s", different in versions:\n'
                           '%s and %s\n'
                           'Fix it adding the version you want to your "%s" file'
                            % (resource.name, version, old_item.version, BIICODE_FILE))
            biiout.warn('Using version "%s" while you fix it' % (old_item.version, ))
        else:
            self[resource.name] = ClosureItem(resource, version)

    def bii_config(self):
        bii_configs = {}
        for block_cell_name, (resource, _) in self.iteritems():
            if block_cell_name.cell_name == 'biicode.conf':
                try:
                    content_ = resource.content.load.text
                    bii_config = BiiConfig(content_)
                except ConfigurationFileError as e:
                    raise ConfigurationFileError('%s: Line %s'
                                                 % (block_cell_name, str(e)))
                bii_configs[block_cell_name.block_name] = bii_config
        return bii_configs
