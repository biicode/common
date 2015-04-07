from biicode.common.edition.parsing.parser import Parser
from biicode.common.model.declare.cpp_declaration import CPPDeclaration
from biicode.common.model.declare.data_declaration import DataDeclaration
from biicode.common.edition.parsing.file_parser import FileParser


class DRLCPPParser(Parser):

    def __init__(self):
        self.declarations = set()
        self.definitions = set()
        self.includes = []
        self.references = []
        self.tags = {}

    @property
    def explicit_declarations(self):
        result = set()
        result |= (set([CPPDeclaration(x.name) for x in self.includes]))
        result |= (set([DataDeclaration(x.name) for x in self.references]))
        return result

    def parse(self, code):
        parser = FileParser()
        self.includes, self.references, self.declarations, self.definitions, \
            self.tags = parser.parse(code)

    def has_main_function(self):
        for definition in self.definitions:
            if definition.name == 'main' and not definition.scope:
                return True
        return False

    def updateDeclaration(self, text, decl, newDecl):
        updated = False
        if isinstance(decl, CPPDeclaration):
            refs = self.includes
        else:
            refs = self.references
        for b in refs:
            if b.name == decl.name:
                old = text[b.start:b.end]
                subs = newDecl.name
                text = '%s%s%s' % (text[:b.start], subs, text[b.end:])  # .replace(old, subs, 1)
                offset = len(subs) - len(old)
                for other in self.includes + self.references:
                    if other.start > b.end:
                        other.start += offset
                        other.end += offset
                updated = True
                b.name = newDecl.name
        if updated:
            return text
        return None
