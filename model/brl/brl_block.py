from biicode.common.model.brl.brl_user import BRLUser
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.brl.group_name import BranchName
from biicode.common.exception import InvalidNameException
from biicode.common.model.brl.complex_name import ComplexName


class BRLBlock(str):

    tmp_regex = '{brl_user}\/{brl_user}\/{complex_name}\/{complex_name}'
    base_er = tmp_regex.format(brl_user=BRLUser.base_er,
                               complex_name=ComplexName.base_er)

    def __new__(cls, name, validate=True):
        '''user/modname/branch
           ie: owner/[originalowner/name]/branch
        '''
        assert isinstance(name, basestring), '%s is not a string' % str(name)
        if not validate:
            obj = str.__new__(cls, name)
        else:
            name = name.strip().replace('\\', '/')
            tokens = name.split('/')
            if len(tokens) != 4:
                raise InvalidNameException("Invalid block name: %s, it should be in the form "
                                           "owner/originalowner/name/branch" % name)
            user = tokens[0]
            block_name = '/'.join(tokens[1:3])
            obj = str.__new__(cls, '%s/%s/%s' % (user, block_name, tokens[3]))
            obj._user = BRLUser(user)
            obj._block_name = BlockName(block_name)
            obj._branch = ComplexName(tokens[3].lower())
        return obj

    def _parse(self):
        tokens = self.split('/')
        self._user = BRLUser(tokens[0], False)
        self._block_name = BlockName('/'.join(tokens[1:3]), False)
        self._branch = tokens[3]

    def __add__(self, obj):
        '''Adding a BRLBlock and a integer, gives as a BlockVersion.
           Adding a BRLBlock and a CellName, gives as a BlockCellName.
        This is a convenience method for easy creation of BlockVersion and BlockCellName,
        not intended for intensive creation use'''
        if isinstance(obj, int):  # obj is an int
            from biicode.common.model.symbolic.block_version import BlockVersion
            return BlockVersion(self, obj)
        else:  # obj is a CellName, return a BlockCellName
            from biicode.common.model.brl.block_cell_name import BlockCellName
            return BlockCellName(self.block_name + str(obj))

    @property
    def owner(self):
        try:
            return self._user
        except:
            self._parse()
            return self._user

    @property
    def branch(self):
        try:
            return self._branch
        except:
            self._parse()
            return self._branch

    @property
    def block_name(self):
        try:
            return self._block_name
        except:
            self._parse()
            return self._block_name

    @property
    def creator(self):
        return self.block_name.user

    @property
    def owner_branch(self):
        return BranchName('%s/%s' % (self.owner, self.branch), False)

    @property
    def is_branched(self):
        return self.branch != "master"

    @property
    def master(self):
        return BRLBlock("%s/%s/master" % (self.creator, self.block_name), False)

    @property
    def master_brl(self):
        if not self.is_branched:
            return self
        return self.block_name + BranchName("%s/%s" % (self.creator, "master"))

    def to_pretty(self, hide_branch=True):
        if self.owner == self.creator:
            if hide_branch and self.branch == 'master':
                return self.block_name
            else:
                return '%s(%s)' % (self.block_name, self.branch)
        else:
            return '%s(%s/%s)' % (self.block_name, self.owner, self.branch)

    @staticmethod
    def deserialize(data):
        return BRLBlock(data, False)

    def serialize(self):
        return self[:]  # => str(self) is slower
