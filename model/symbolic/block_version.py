from collections import namedtuple
from biicode.common.model.brl.brl_block import BRLBlock
from biicode.common.model.brl.block_name import BlockName
from biicode.common.model.brl.group_name import BranchName
from biicode.common.exception import BiiException
import re
from biicode.common.model.brl.complex_name import ComplexName


def _build_block_version_re():
    # "lasote/block" is a BlockName.base_er
    block_name_er = "{block_name}".format(block_name=BlockName.base_er)
    # "lasote/branch" or just "branch" is a branch_name or just a complexname
    branch_er = "({branch_name})|({complex_name})".format(branch_name=BranchName.base_er,
                                                          complex_name=ComplexName.base_er)
    # Comments at the end of line
    comments = "(#.*)?"
    # Spaces
    spaces = "\s*"

    # ?P<blockname> is for extract matching group values in a dict with "blockname" key
    tmp = "{spaces}(?P<block_name>{block_name_er})"  # Spaces following a block name
    tmp += "{spaces}(\((?P<branch>{branch_er})\))?"  # Optional branch name
    # Optional time ":2323" \d* => natural numbers or -1
    tmp += "{spaces}(:{spaces}(?P<time>(\d*|-1)))?"
    # Optional version tag "@something" => .* all chars are valid
    tmp += "{spaces}(@{spaces}(?P<tag>.*))?"
    tmp += "{spaces}{comments}"  # Comments at the end of the line
    tmp = tmp.format(**locals())
    tmp = r"^%s$" % tmp
    return re.compile(tmp)

block_version_re = _build_block_version_re()


def parse_block_version_expression(text):
    '''Parse text and returns the components of a BlockVersion

    Valid text input examples:
        lasote/myblock
        lasote/myblock(master)
        lasote/myblock(master):1
        lasote/myblock(pepe/branch):33 @My cool version # Comment at the end
    '''

    text = text.strip().replace('\\', '/')
    group_values = [m.groupdict() for m in block_version_re.finditer(text)]
    if len(group_values) == 0:  # Not Match
        raise ValueError()

    group_values = group_values[0]

    # Get block_name
    block_name = BlockName(group_values["block_name"])

    # Get complete branch_name
    if group_values.get("branch", None) is None:  # If none => owner/master
        branch_user = block_name.user
        branch_name = "master"
    elif "/" in group_values["branch"]:
        branch_user, branch_name = group_values["branch"].split("/")
    else:  # Only branch_name, so owner/branch_name
        branch_user = block_name.user
        branch_name = group_values["branch"]
    branch = BranchName('%s/%s' % (branch_user, branch_name))
    brl_block = BRLBlock('%s/%s/%s/%s' % (branch.user, block_name.user,
                                          block_name.name, branch.name))
    # Get time
    version = group_values.get("time", None)
    time = int(version) if version else None
    version_tag = group_values.get("tag", None)

    return brl_block, time, version_tag


class BlockVersion(namedtuple('BlockVersion', ['block', 'time', 'tag'])):
    '''A blockVersion is BRLBlock with a 0-based time index'''
    def __new__(cls, block, time, tag=None):
        if not isinstance(block, BRLBlock):
            block = BRLBlock(block)
        return super(BlockVersion, cls).__new__(cls, block, time, tag)

    @property
    def block_name(self):
        return self.block.block_name

    @classmethod
    def loads(cls, text):
        try:
            brl_block, time, tag = parse_block_version_expression(text)
            return cls(brl_block, time, tag)
        except ValueError:
            raise BiiException('Bad block version format "%s", '
                               'it should be in the form user/block[([track_user/]track)]'
                               '[:version][ @version_tag]' % text)

    def __add__(self, cell_name):
        '''Adding a BlockVersion+CellName gives as a Reference. This is a
        convenience method for easy creation of Reference, not intended for
        intensive creation use'''
        from biicode.common.model.symbolic.reference import Reference
        return Reference(self, cell_name)

    def __repr__(self):
        return self.to_pretty()

    def to_pretty(self, hide_branch=True):
        if self.time is not None:
            pretty = '%s: %d' % (self.block.to_pretty(hide_branch), self.time)
        else:
            pretty = self.block.to_pretty(hide_branch)
        if self.tag is not None:
            return '%s @%s' % (pretty, self.tag)
        return pretty

    @staticmethod
    def deserialize(data):
        return BlockVersion(BRLBlock.deserialize(data[0]), *data[1:])

    def serialize(self):
        return self.block.serialize(), self.time

    def __eq__(self, other):
        '''version tag is not used in eq comparison'''
        if other is None:
            return False
        if isinstance(other, self.__class__):
            return other.block == self.block and other.time == self.time
        return False

    def __hash__(self):
        return hash((self.block, self.time))

    def __ne__(self, other):
        return not self.__eq__(other)
