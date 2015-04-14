
import ast
import _ast


class PythonAst(ast.NodeVisitor):

    PYTHON_C_MODULE = 'link_clib'

    def __init__(self):
        self.objects = []
        self.c_includes = []
        self.hasmain = False

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Import(self, node):
        pos = (node.lineno, node.col_offset)
        for i in node.names:
            if i.asname is None:
                self.objects.append(('import', pos, i.name, 'import', ('import ' + i.name)))
            else:
                self.objects.append(('import', pos, i.asname, 'import',
                                     ('import ' + i.name + " as " + i.asname)))

    def visit_ImportFrom(self, node):
        pos = (node.lineno, node.col_offset)
        for i in node.names:
            if i.asname is None:
                self.objects.append(('from', pos, i.name, 'import',
                                     ('from ' + node.module + ' import ' + i.name)))
            else:
                self.objects.append(('from', pos, i.asname, 'import',
                                     ('from ' + node.module + ' import ' + i.name
                                      + ' as ' + i.asname)))

    def visit_Call(self, node):
        if self.visit(node.func):
            self.c_includes.append(node.args[0].s)

    def visit_Assign(self, node):
        self.visit(node.value)

    def visit_Name(self, node):
        return node.id == self.PYTHON_C_MODULE

    def visit_Attribute(self, node):
        return node.attr == self.PYTHON_C_MODULE
