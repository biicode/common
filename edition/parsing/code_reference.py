from collections import namedtuple


class CodeReference():
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and self.start == other.start and self.end == other.end

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '%s [%s - %s]' % (self.name, self.start, self.end)


class CPPItem(namedtuple('CPPItem', 'type name scope')):
    '''either a declaration or a definition of something in c/c++
    type: Class, Struct, Method or Var
    name: The non-namespace qualified name
    scope: The aggregated namespace as string NS1::NS2::MyClass'''
    CLASS = 'c'
    STRUCT = 's'
    METHOD = 'm'
    VAR = 'v'

    def __new__(cls, type_, name, scope=None):
        return super(CPPItem, cls).__new__(cls, type_, name, scope or '')

    @staticmethod
    def extend_scope(scope, scop):
        if scope and scop:
            return '%s::%s' % (scope, scop)
        return scope or scop
