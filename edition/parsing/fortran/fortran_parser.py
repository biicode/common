from biicode.common.edition.parsing.parser import Parser
from biicode.common.model.declare.data_declaration import DataDeclaration
from biicode.common.edition.parsing.fortran.fortran_file_parser import FortranFileParser
from biicode.common.model.declare.fortran_declaration import FortranDeclaration
from biicode.common.model.deps_props import DependenciesProperties


class FortranParser(Parser):

    def __init__(self):
        self.includes = []
        self.references = []
        self.declarations = set()
        self.definitions = set()
        self.modules = set()
        self.parser = FortranFileParser()
        self.comments = []

    @property
    def explicit_declarations(self):
        result = set()
        result |= (set([FortranDeclaration("%s%s.f90" % (x.scope, x.name)) for x in self.modules]))
        includes = set([FortranDeclaration(x.name) for x in self.includes])
        for inc in includes:
            inc.properties.add(DependenciesProperties.EXCLUDE_FROM_BUILD)
        result |= includes
        result |= (set([DataDeclaration(x.name) for x in self.references]))
        return result

    @property
    def include_declarations(self):
        result = set()
        result |= (set([FortranDeclaration(x.name, True) for x in self.includes]))
        return result

    def parse(self, code):
        try:
            self.parser.parse(code)
            self.definitions = self.parser.definitions
            self.declarations = self.parser.declarations
            self.includes = self.parser.includes
            self.references = self.parser.references
            self.modules = self.parser.modules
        except:
            pass

    def has_main_function(self):
        return False

    def findImplicit(self, other):
        for declaration in self.declarations:
            for definition in other.definitions:
                if declaration.match(definition):
                    return True
        for module in self.modules:
            for definition in other.definitions:
                if module.match(definition):
                    return True

    def updateDeclaration(self, text, decl, newDecl):
        updated = False
        if isinstance(decl, FortranDeclaration):
            refs = self.includes
        else:
            refs = self.references
        for b in refs:
            if b.name == decl.name:
                old = text[b.start:b.end]
                subs = newDecl.name
                text = '%s%s%s' % (text[:b.start], subs, text[b.end:]) # .replace(old, subs, 1)
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

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.modules == other.modules

    def __ne__(self, other):
        return not self.__eq__(other)
