import fnmatch
from biicode.common.exception import BiiException
from biicode.common.model.bii_type import BiiType, CMAKE
import os


class TypeFilter(list):
    ''' a list of rules, each one tuple (pattern, accept)'''

    def __add__(self, other):
        result = TypeFilter()
        result.extend(self)
        result.extend(other)
        return result

    @staticmethod
    def loads(text):
        result = TypeFilter()
        for (line_no, line) in enumerate(text.splitlines()):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                tokens = line.split()
                biitype = BiiType.from_text(tokens[1]) if len(tokens) > 1 else None
                result.append((tokens[0], biitype))  # Pattern, extension
            except Exception:
                raise BiiException('Wrong type format in line %d: %s' % (line_no, line))
        return result

    def type(self, name):
        result = None
        for pattern, biitype in self:
            if pattern == 'NOEXT':
                if os.path.splitext(name)[1] == '':
                    result = biitype
            elif fnmatch.fnmatch(name, pattern):
                result = biitype
        if result is None:
            if "CMakeLists.txt" in name:
                result = BiiType(CMAKE)
            else:
                extension = os.path.splitext(name)[1]
                result = BiiType.from_extension(extension)
        return result
