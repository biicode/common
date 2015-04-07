from biicode.common.edition.parsing.parser import Parser
from biicode.common.model.declare.cmake_declaration import CMakeDeclaration
from biicode.common.edition.parsing.cmake.cmake_file_parser import CMakeFileParser


class CMakeParser(Parser):

    def __init__(self):
        self.includes = []

    @property
    def explicit_declarations(self):
        result = set()
        result |= (set([CMakeDeclaration(x.name) for x in self.includes]))
        return result

    def has_main_function(self):
        return False

    def parse(self, code):
        parser = CMakeFileParser()
        self.includes = parser.parse(code)

    def updateDeclaration(self, text, decl, newDecl):
        return None
