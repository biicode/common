from biicode.common.exception import BiiException
import ast
import _ast
from collections import namedtuple
from biicode.common.model.brl.cell_name import CellName
import re
from biicode.common.model.brl.complex_name import ComplexName


VirtualParseResult = namedtuple('VirtualParseResult', ['code', 'leaves', 'apply'])


class VirtualParserException (BiiException):
    pass


def parse_validate_virtual_func(node):

    class ReturnParser(ast.NodeVisitor):
        leaves = set()
        lastLine = -1

        def visit_Return(self, node):
            if not isinstance(node.value, _ast.Str):
                raise BiiException('Bad virtual file, returning other than string')
            ret = ComplexName(node.value.s)
            self.leaves.add(ret)
            self.lastLine = node.lineno

        def visit_Import(self, imp):
            raise BiiException('Bad virtual file, no imports allowed')

        def visit_Exec(self, imp):
            raise BiiException('Bad virtual file, no exec allowed')

        def visit_Name(self, name):
            self.lastLine = node.lineno

        def generic_visit(self, node):
            try:
                self.lastLine = node.lineno
            except:
                pass
            super(ReturnParser, self).generic_visit(node)

    # print node.args.args
    if len(node.args.args) != 1 or node.args.args[0].id != 'settings':
        raise BiiException('Virtual functions should only have one "settings" parameter')

    # dump=ast.dump(tree)
    # print dump
    parser = ReturnParser()
    parser.visit(node)
    return node.name, parser.lastLine, parser.leaves


def parseFile(code):
    files_sep_pattern = re.compile(r'[^,;\s]+')

    class GlobalParser(ast.NodeVisitor):
        result = {}

        def visit_FunctionDef(self, node):
            doc_string = None
            try:
                (name, lastLine, leaves) = parse_validate_virtual_func(node)
                code_lines = code.splitlines()[node.lineno - 1:lastLine]
                code_lines[0] = code_lines[0].replace(name, 'virtual')
                virtual_logic = '\n'.join(code_lines)
                doc_string = ast.get_docstring(node)
                filenames = files_sep_pattern.findall(doc_string)
                cells_to_apply = {CellName(item) for item in filenames}
                r = VirtualParseResult(virtual_logic, leaves, cells_to_apply)
                self.result[name] = r
            except BiiException as e:
                raise e
            except Exception as e:
                if doc_string is None:
                    raise VirtualParserException('Missing docstring in virtual config definition')
                raise VirtualParserException('There was an error while parsing virtual.bii file '
                                             '%s' % str(e))

        def visit_Module(self, m):
            super(GlobalParser, self).generic_visit(m)

        def generic_visit(self, imp):
            #print imp
            raise VirtualParserException('Bad virtual file, not allowed instruction %s at line %d'
                                         % (imp.lineno, imp.lineno))
    try:
        t = ast.parse(code)
    except Exception as e:
        raise VirtualParserException('There was an error while parsing virtual.bii file '
                                     '%s' % str(e))
    parser = GlobalParser()
    parser.visit(t)

    # TODO: Check here that no 2 rules are applied to the same item
    return parser.result
