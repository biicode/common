from biicode.common.model.brl.group_name import GroupName, BranchName


class BlockName(GroupName):
    '''user/block'''
    def __add__(self, x):
        from cell_name import CellName
        from block_cell_name import BlockCellName
        if isinstance(x, CellName):
            m = BlockCellName('%s/%s' % (self, x), False)
            m._block = self
            m._cell = x
        elif isinstance(x, BranchName):
            from brl_block import BRLBlock
            m = BRLBlock('%s/%s/%s' % (x.user, self, x.name), False)
        elif isinstance(x, basestring):
            m = BlockCellName('%s/%s' % (self, x))
        else:
            raise ValueError("Unknown type {}".format(x.__class__.__name__))

        return m

    def default_block(self):
        from biicode.common.model.brl.brl_block import BRLBlock
        return BRLBlock("%s/%s/master" % (self.user, self), validate=False)

    def init_version(self):
        from biicode.common.model.symbolic.block_version import BlockVersion
        return BlockVersion(self.default_block(), -1)
