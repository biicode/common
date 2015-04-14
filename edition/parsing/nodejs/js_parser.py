from biicode.common.edition.parsing.parser import Parser
from biicode.common.model.declare.node_declaration import NodeDeclaration
from biicode.common.model.declare.data_declaration import DataDeclaration
from biicode.common.edition.parsing.nodejs.node_file_parser import NodeFileParser


class NodeJSParser(Parser):

    def __init__(self):
        self.requires = []
        self.references = []
        self.comments = []

    @property
    def explicit_declarations(self):
        result = set()
        result |= (set([NodeDeclaration(x.name) for x in self.requires]))
        result |= (set([DataDeclaration(x.name) for x in self.references]))
        return result

    def parse(self, code):
        parser = NodeFileParser()
        self.requires, self.references, _, _, self.comments = parser.parse(code)

    def has_main_function(self):
        return False    # TODO: exe main file or command file

    def updateDeclaration(self, text, decl, newDecl):
        updated = False
        if isinstance(decl, NodeDeclaration):
            refs = self.requires
        else:
            refs = self.references
        for b in refs:
            if b.name == decl.name:
                old = text[b.start:b.end]
                subs = newDecl.name
                text = '%s%s%s' % (text[:b.start], subs, text[b.end:]) # .replace(old, subs, 1)
                offset = len(subs) - len(old)
                for other in self.requires + self.references:
                    if other.start > b.end:
                        other.start += offset
                        other.end += offset
                updated = True
                b.name = newDecl.name
        if updated:
            return text
        return None

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.modules == other.modules

    def __ne__(self, other):
        return not self.__eq__(other)
