from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.exception import BiiException
from biicode.common.edition.parsing.conf.conf_file_parser import parse


def parent_loads(text, line_number):
    """ return a BlockVersion if found, or None. If no time is present, return -1 as timestep
    raise BiiException on parse errors
    """
    result = []

    def parents_line_parser(line):
        if line.startswith('*'):
            line = line[1:]

        version = BlockVersion.loads(line)
        if result:
            raise BiiException('Impossible to have two main parents')

        result.append(version)
    parse(text, parents_line_parser, line_number)
    if result and result[0].time is None:
        return BlockVersion(result[0].block, -1)
    return result[0] if result else None
