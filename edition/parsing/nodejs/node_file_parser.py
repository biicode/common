"""NodeJs File Parser."""
from biicode.common.edition.parsing.file_parser import FileParser
from biicode.common.edition.parsing.code_reference import CodeReference
from biicode.common.utils.bii_logging import logger
import re
from biicode.common.edition.parsing.conf.comments_tags_parser import parse_tags


def require_in_comments(require_start, comments):
    """Return True if require is within a comment."""
    for comment in comments:
        if require_start >= comment.start and require_start <= comment.end:
            return True


class NodeFileParser(FileParser):

    REQUIRE = 'REQUIRE'

    limits = {'//': ('\n', FileParser.COMMENT),
              '/*': ('*/', FileParser.MULTILINE),
              '"': ('"', FileParser.TEXT),
              '#': ('\n', FileParser.PREPROCESSOR),
              ' require ': (')', REQUIRE),
              '=require ': (')', REQUIRE),
              ' require(': (')', REQUIRE),
              '=require(': (')', REQUIRE)}

    initial_pattern = re.compile(r'//|#|/[*]')
    require_pattern = re.compile(r'(?:\s|\=|\()require\s*\(\s*(?:\"|\')(.+?)(?:\"|\')\s*\)')
    bii_data_pattern = re.compile(r"(?://|/*)\s*bii://(.*)")
    start_require_pattern = re.compile(r'"|\'')

    def _extract_symbols(self, code):
        '''overwrite of extract_symbols, returning None Declarations and None Definitions'''
        return None, None

    def parse(self, code):
        """main entry point for parsing the text "code".

        return tuple(requires(list),
                     references(list),
                     declarations(set),
                     definitions(set),
        tags(dict))

        """
        #This 2 lines where in normalizing Blob. A final \n is required for some things to be
        #correctly parsed
        if not code.endswith('\n'):
            code = '%s\n' % code

        result, _ = self._parse_strings_comments(code)
        comments = [comment for comment in result if comment.type in (FileParser.COMMENT, FileParser.MULTILINE)]

        requires = self._parse_requires(code, comments)

        references = self._parse_references(code)
        comments = self.parse_comments(result)
        tags = parse_tags(comments) # parse all biicode tags, comments with "bii:#"
        return requires, references, [], [], tags

    def _parse_requires(self, code, comments):
        requires = []

        for require_match in self.require_pattern.finditer(code):
            require = require_match.group(1)
            require_start = require_match.start(1)
            require_end = require_match.end(1)
            if not require_in_comments(require_start, comments):
                requires.append(CodeReference(require, require_start, require_end))

        return requires

    def _parse_references(self, code):
        references = []
        for bii_data_match in self.bii_data_pattern.finditer(code):
            reference = bii_data_match.group(1)
            ref_start = bii_data_match.start(1)
            ref_end = bii_data_match.end(1)
            references.append(CodeReference(reference, ref_start, ref_end))

        return references

    def handle_preprocessor(self, text):
        closer = {'"': '"',
                  '\'': '\''}
        tokenized_code = self.tokenize_code(text)
        if 'require' == tokenized_code[0] or 'require' == tokenized_code[1]:  # TODO: Do not tokenize the full preprocesor directive
            try:
                m = self.start_require_pattern.search(text)
                start = m.start() + 1
                c = closer[m.group()]
                end = text.find(c, start + 1)
                return start, end, text[start:end].strip()
            except:
                logger.error('Unable to parse require %s ' % text)
        return (None, None, None)
