from biicode.common.edition.parsing.conf.conf_file_parser import parse
from collections import namedtuple


def parse_mains_conf(text, line_number):
    mains = []

    def path_line_parser(line):
        mains.append(EntryPointConfiguration.parse(line))

    parse(text, path_line_parser, line_number)
    return mains


class EntryPointConfiguration(namedtuple("EntryPoint", "name has_main")):

    EXCLUDE_FLAG = '!'

    @classmethod
    def parse(cls, line):
        if line[0] == cls.EXCLUDE_FLAG:
            name = line[1:].strip()
            has_main = False
        else:
            name = line.strip()
            has_main = True
        return cls(name, has_main)
