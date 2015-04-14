from collections import namedtuple


class FItem(namedtuple('FItem', 'type name scope')):
    MODULE = 'module'
    SUBRUTINE = 'subroutine'
    CALL = 'call'
    USE = 'use'
    SUBPROGRAM = 'subprogram'

    def __new__(cls, type_, name, scope=None):
        if scope is None:
            scope = ""
        obj = super(FItem, cls).__new__(cls, type_, name, scope)
        return obj

    def __hash__(self):
        return hash((self.type, self.name))

    def match(self, definition):
        if self.type == FItem.SUBPROGRAM:
            return self.name == definition.name
        if self.type == FItem.MODULE or self.type == FItem.SUBRUTINE:
            try:
                if self.name == definition.name:  # class name match
                    return True  # TODO: Check here full scope?
            except:
                pass
        if self.type == FItem.CALL or self.type == FItem.USE:
            if self.name == definition.name and self.scope == definition.scope:
                return True

        # FIXME: Complete match
