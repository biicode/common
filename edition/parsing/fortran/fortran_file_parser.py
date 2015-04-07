from biicode.common.edition.parsing.file_parser import FileParser
from biicode.common.utils.bii_logging import logger
import re
from biicode.common.edition.parsing.code_reference import CodeReference
from biicode.common.edition.parsing.fortran.fortran_code_ref import FItem


class FortranFileParser(FileParser):

    CALL = 'SUBPROGRAM'
    USE = 'MODULE'
    INCLUDE = 'INCLUDE'
    DEF_SUB = 'DEF_SUBPROGRAM'
    DEF_MODULE = 'DEF_MODULE'

    limits = {'!': ('\n', FileParser.COMMENT),
              '"': ('"', FileParser.TEXT),
              "'": ("'", FileParser.TEXT),
                'subroutine ': ('\n', DEF_SUB),
                'module ': ('\n', DEF_MODULE),
                'call ': ('\n', CALL),
                'include ': ('\n', INCLUDE),
                'use ': ('\n', USE)}

    initial_pattern = re.compile(r'//|#|"|!|/[*]|subroutine |module |call |use |include ')

    def __init__(self, content=None):
        self.includes = []
        self.references = []
        self.modules = set()
        self.declarations = set()
        self.definitions = set()
        self.content = content
        self.has_main_function = False

    def parse(self, code):
        result, clean_code = self._parse_strings_comments(code.lower())
        self.has_main_function = self.mainFunction(clean_code)
        self.parse_references(result)

    def mainFunction(self, code):
        tokenized_code = self.tokenize_code(code.upper())
        if len(tokenized_code) == 0:
            return False
        return tokenized_code[0] == 'PROGRAM'

    def parse_references(self, result):
        for item in result:
            if item.type == self.INCLUDE:
                begin, end, deps = self.handle_preprocessor(item.content)
                if deps:
                    self.includes.append(CodeReference(deps, item.start+begin, item.start+end))

            if item.type == self.USE:
                scope = self.scope_preprocessor(item.content)
                name = self.name_preprocessor(item.content)
                self.modules.add(FItem('module', name, scope))

            if item.type == self.CALL:
                scope = self.scope_preprocessor(item.content)
                name = self.name_preprocessor(item.content)
                self.declarations.add(FItem('subprogram', name, scope))

            if item.type == self.DEF_SUB:
                scope = self.scope_preprocessor(item.content)
                name = self.name_preprocessor(item.content)
                self.definitions.add(FItem('subprogram', name, scope))

            if item.type == self.DEF_MODULE:
                scope = self.scope_preprocessor(item.content)
                name = self.name_preprocessor(item.content)
                self.definitions.add(FItem('module', name, scope))

            if item.type == self.COMMENT:
                data = self.handle_comment(item.content)
                if data:
                    # +2, -1 to account for // and line ending
                    self.references.append(CodeReference(data, item.start+len(FileParser.BII_DATA_REF)+2, item.end-1))

    start_require_pattern = re.compile(r'\'|"|!')

    def handle_preprocessor(self, text):
        closer = {'"': '"',
                  "'": "'"}
        tokenized_code = self.tokenize_code(text)
        if 'INCLUDE' == tokenized_code[0] or 'include' == tokenized_code[0]:
            try:
                m = self.start_require_pattern.search(text)
                start = m.start() + 1
                c = closer[m.group()]
                end = text.find(c, start + 1)
                return start, end, text[start:end].strip()
            except:
                logger.error('Unable to parse require %s ' % text)
        return (None, None, None)

    def scope_preprocessor(self, text):
        tokenized_code = self.tokenize_code(text)
        if 'call' == tokenized_code[0] or 'use' == tokenized_code[0]:
            try:
                m = self.start_require_pattern.search(text)
                if m:
                    start = m.start() + 1
                    for index, token in enumerate(tokenized_code):
                        if token == "!":
                            end = text.find("\n")
                return text[start:end].strip()
            except:
                pass
        return None

    def name_preprocessor(self, text):
        tokenized_code = self.tokenize_code(text)
        name = ''
        for items in tokenized_code[1:]:
            if items == "\n" or items == "!" or items == "(":
                return name
            name = name + items
        return name
