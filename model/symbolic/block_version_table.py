from biicode.common.model.symbolic.block_version import BlockVersion
from biicode.common.utils.serializer import ListDeserializer, serialize
from biicode.common.exception import BiiException
from biicode.common.edition.parsing.conf.conf_file_parser import parse


class BlockVersionTable(dict):
    '''a dict {BlockName: BlockVersion}'''
    def __init__(self, versions=None):
        if versions:
            for version in versions:
                self.add_version(version)

    def copy(self):
        return BlockVersionTable(self.itervalues())

    def add_version(self, block_version):
        self[block_version.block.block_name] = block_version

    @classmethod
    def loads(cls, text, line_number=0):
        """ loads from text a table, the text might have comments with #
        raises BiiException in case of file error, conflicts or duplicated dependencies
        return: BlockVersionTable
        """
        result = cls()
        if not text:
            return result

        def table_line_parser(line):
            version = BlockVersion.loads(line)
            if version.block_name in result:
                raise BiiException('Duplicate dependency "%s"' % version.to_pretty())
            result.add_version(version)

        parse(text, table_line_parser, line_number)
        return result

    def dumps(self, text=""):
        """ dumps the contents to a text string (with \n LF), if optional param text is passed
        it tries to maintain the comments and structure of such text
        return: text translation of self
        """
        if text:
            result = []
        else:
            result = ['# This file contains your block external dependencies references']
        replaced_versions = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):  # Blank and comment lines
                result.append(line)
                continue
            try:
                current_version = BlockVersion.loads(line)
                version = self.get(current_version.block_name)
                if version:
                    result.append(str(version))
                    replaced_versions.append(version)
            except:
                result.append(line)
                continue
        for version in self.itervalues():
            if version not in replaced_versions:
                result.append(str(version))
        result.append('')
        return '\n'.join(result)

    def __repr__(self):
        return "\n".join([bv.to_pretty(False) for bv in self.itervalues()])

    @staticmethod
    def deserialize(data):
        if data is None:
            return None
        versions = ListDeserializer(BlockVersion).deserialize(data)
        table = BlockVersionTable()
        for version in versions:
            table.add_version(version)
        return table

    def serialize(self):
        return serialize(self.values())
