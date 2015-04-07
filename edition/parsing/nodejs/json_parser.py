from json import JSONDecoder
from biicode.common.model.declare.node_declaration import NodeDeclaration
from biicode.common.edition.parsing.parser import Parser


class PackageJSONParser(Parser):

    """Handle package.json of nodejs projects."""

    def __init__(self):
        self.main = None

    def parse(self, code):
        try:
            json_object = JSONDecoder().decode(code)
        except ValueError:
            json_object = {}
        self.main = json_object.get('main')

    def has_main_function(self):
        return False

    def updateDeclaration(self, text, decl, newDecl):
        return text

    @property
    def explicit_declarations(self):
        result = set()
        if self.main:
            result.add(NodeDeclaration(self.main))
        return result

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.main == other.main

    def __ne__(self, other):
        return not self.__eq__(other)
