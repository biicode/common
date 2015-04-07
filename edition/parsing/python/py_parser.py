
from biicode.common.edition.parsing.parser import Parser, BII_DATA_REF
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.model.declare.python_declaration import PythonDeclaration
from biicode.common.model.declare.data_declaration import DataDeclaration
import ast
import tokenize
import cStringIO
import string

from biicode.common.edition.parsing.code_reference import CodeReference
from biicode.common.edition.parsing.python.python_ast import PythonAst


def separecode(code):
    info = string.split(code, '\n')
    textlen = []
    for i in info:
        textlen.append(len(i) + 1)
    return textlen


def position(token_pos_info, textlines, word=None):
    line, pos = token_pos_info
    cont = 0
    for i in textlines[:(line - 1)]:
        cont = cont + i
        if word:
            cont = cont + len(word)
    return cont + pos


class PythonParser(Parser):

    def __init__(self):
        self.imports = []
        self.c_includes = []
        self.references = []
        self.comments = []

    @property
    def explicit_declarations(self):
        result = set()
        result |= (set([PythonDeclaration(x.name) for x in self.imports]))
        result |= (set([CPPDeclaration(x) for x in self.c_includes]))
        result |= (set([DataDeclaration(x.name) for x in self.references]))
        return result

    def parse(self, code):
        node = ast.parse(code)
        parser = PythonAst()
        parser.visit(node)
        self.c_includes = parser.c_includes
        parser_result = []
        self.tokens_filter(parser_result, parser, code)
        self.parse_references(parser_result)

    def tokens_filter(self, parser_result, parser, code):
        textlen = separecode(code)
        output = cStringIO.StringIO(code)
        for type_, name, startoken, endtoken, _ in tokenize.generate_tokens(output.readline):
            start = position(startoken, textlen)
            end = position(endtoken, textlen, name)

            if type_ == tokenize.STRING:
                parser_result.append(['multiline', start, end, name])
            if type_ == tokenize.COMMENT:
                if name.startswith(BII_DATA_REF, 1):
                    parser_result.append(['BII_DATA_REF', start, end, name])
                else:
                    parser_result.append(['comment', start, end, name])

            self.ast_and_tokens_comparator(parser, name, start, startoken, parser_result)

    def ast_and_tokens_comparator(self, parser, token_name, token_start, startoken, parser_result):
        for object_ in parser.objects:
            object_token, object_startoken, _, object_type, object_name = object_

            if object_token == token_name and object_startoken == startoken:
                end_object = token_start + len(object_name)
                parser_result.append([object_type, token_start, end_object, object_name])

    def parse_references(self, parser_result):
        for element in parser_result:
            type_, start, end, name = element
            if type_ == 'import':
                self.imports.append(CodeReference(name, start, end))
            elif type_ == 'BII_DATA_REF':
                self.references.append(CodeReference(name[1:], start, end))

    def has_main_function(self):
        if any(isinstance(exp, CPPDeclaration) for exp in self.explicit_declarations):
            return True

    def updateDeclaration(self, text, decl, newDecl):
        updated = False
        if isinstance(decl, PythonDeclaration):
            refs = self.imports
        else:
            refs = self.references
        for b in refs:
            if decl.name in b.name:
                old = text[b.start:b.end]
                subs = newDecl.name
                text = '%s%s%s' % (text[:b.start], subs, text[b.end:])  # .replace(old, subs, 1)
                offset = len(subs) - len(old)
                for other in self.imports + self.references:
                    if other.start > b.end:
                        other.start += offset
                        other.end += offset
                updated = True
                b.name = newDecl.name
        if updated:
            return text
        return None
