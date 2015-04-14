
from collections import namedtuple


class JSItem(namedtuple('JSItem', 'type name scope')):
    CLASS = 'class'
    STRUCT = 'struct'
    METHOD = 'method'
    VAR = 'var'

    def __new__(cls, type_, name, scope=None):
        if scope == None:
            scope = []
        obj = super(JSItem, cls).__new__(cls, type_, name, scope)
        return obj

    def __hash__(self):
        return hash((self.type, self.name))

    def match(self, definition):
        if self.type == JSItem.CLASS or self.type == JSItem.STRUCT:
            try:
                if self.scope + [self.name] == definition.scope:  # class name match
                    return True  # TODO: Check here full scope?
            except:
                pass
        if self.type == JSItem.METHOD or self.type == JSItem.VAR:
            if self.name == definition.name and self.scope == definition.scope:
                return True

        # FIXME: Complete match
