import ast
from collections import namedtuple


class PythonImport(namedtuple('PythonImport', "module, names, alias")):

    """Store all information relative to python imports.
        Attributes:
        ----------
            module: Module Name.
            names: list of tuples ("name", "alias"=None)
            alias: Module alias. Default None.
    """

    def __new__(cls, module=None, names=None, alias=None):
        return super(PythonImport, cls).__new__(cls, module, names, alias)

    @property
    def names_with_alias(self):
        """Return an array of name or aliased name. This method is necessary because self.names is an array of tuples
           so for some transformation this approach is more suitable.
           :return, list("name", "name as alias", ...)
        """
        names = []
        for name, alias in self.names:
            name = "%s" % name
            if alias:
                name += " as %s" % alias
            names.append(name)
        return names

    @staticmethod
    def parse(name):
        try:
            node = ast.parse(name)
        except SyntaxError:
            return None
        visitor = ImportsVisitor()
        visitor.visit(node)
        python_import = visitor.objects[0]
        return python_import

    def to_python_statement(self):
        """Transform PythonImport structure to standar python."""
        if self.names:
            declaration = "from %s import %s" % (self.module, ", ".join(self.names_with_alias))
        else:
            declaration = "import %s" % self.module
            if self.alias:
                declaration += " as %s" % self.alias
        return declaration

    def is_composed_module(self):
        return "." in self.module

    def is_aliasable(self):
        """Python imports should be aliased only with one alias. Also if import is already aliased it mustn't be
            substituded. Return a boolean."""
        return self.alias is None and self.names is None and not self.is_composed_module()

    def __eq__(self, other):
        return self.names == other.names and self.module == other.module and self.alias == other.alias

    def __ne__(self, other):
        return not self.__eq__(other)


class ImportsVisitor(ast.NodeVisitor):
    def __init__(self):
        self.objects = []

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Import(self, node):
        for i in node.names:
            self.objects.append(PythonImport(module=i.name, alias=i.asname))

    def visit_ImportFrom(self, node):
        names = []
        for i in node.names:
            names.append((i.name, i.asname))
        self.objects.append(PythonImport(module=node.module, names=names))
