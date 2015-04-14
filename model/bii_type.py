UNKNOWN = 0
TEXT = 1
IMAGE = 2
SOUND = 3
HTML = 4
XML = 5
CPP = 6
PYTHON = 7
JS = 8
JAVA = 9
FORTRAN = 10
JSON = 11
CMAKE = 12


class BiiType(int):

    _ext_dict = {".h":    CPP,
                 ".hh":   CPP,
                 ".hxx":  CPP,
                 ".hpp":  CPP,
                 ".c":    CPP,
                 ".cc":   CPP,
                 ".cpp":  CPP,
                 ".cxx":  CPP,
                 ".c++":  CPP,
                 ".inl":  CPP,
                 ".ino":  CPP,
                 ".ipp":  CPP,
                 ".txt":  TEXT,
                 ".xml":  XML,
                 ".html": HTML,
                 ".htm":  HTML,
                 ".wav":  SOUND,
                 ".jpg":  IMAGE,
                 ".jpeg":  IMAGE,
                 ".gif":  IMAGE,
                 ".png":  IMAGE,
                 ".bmp":  IMAGE,
                 ".py":   PYTHON,
                 ".bii":  TEXT,
                 ".md":  TEXT,
                 ".js": JS,
                 ".node": JS,
                 ".json": JSON,
                 ".java": JAVA,
                 ".f": FORTRAN,
                 ".for": FORTRAN,
                 ".f90": FORTRAN,
                 ".cmake": CMAKE,
                 ".conf": TEXT,
                 ".yml": TEXT}

    _binary_types = (SOUND, IMAGE, UNKNOWN)
    _cpp_header_exts = (".h", ".hh", ".hxx", ".hpp")
    cpp_src_exts = (".c", ".cc", ".cpp", ".cxx", ".c++", ".m")  # FIXME: temporal solution .m

    def is_binary(self):
        return self in self._binary_types

    @classmethod
    def isCppHeader(cls, extension):
        return extension in cls._cpp_header_exts

    @classmethod
    def is_cpp_source(cls, extension):
        return extension in cls.cpp_src_exts

    @classmethod
    def from_extension(cls, extension):
        """ @param extension with point ".jpg", ".cpp"
            @return BiiType or UNKNOWN
        """
        num = cls._ext_dict.get(extension, UNKNOWN)
        return BiiType(num)

    @classmethod
    def from_content(cls, content):
        """ Check if any content is binary or string
            @param content as string
            @return UNKNOWN or TEXT
        """
        from biicode.common.utils.file_utils import is_binary_string
        if is_binary_string(content):
            return BiiType(UNKNOWN)
        else:
            return BiiType(TEXT)

    @classmethod
    def from_text(cls, text):
        _bii_types = {'CPP': cls(CPP),
                      'JAVA': cls(JAVA),
                      'IMAGE': cls(IMAGE),
                      'TEXT': cls(TEXT),
                      'PYTHON': cls(PYTHON),
                      'FORTRAN': cls(FORTRAN),
                      'JS': cls(JS),
                      'HTML': cls(HTML),
                      'CMAKE': cls(CMAKE)}
        num = _bii_types[text.upper()]
        return BiiType(num)

    def __repr__(self):
        return {0: 'UNKNOWN', 1: 'TEXT', 2: 'IMAGE', 3: 'SOUND', 4: 'HTML', 5: 'XML',
                6: 'CPP', 7: 'PYTHON', 8: 'JS', 9: 'JAVA', 10: 'FORTRAN', 11: 'JSON',
                12: 'CMAKE'}[self]

    def __str__(self):
        return repr(self)

    def serialize(self):
        return  int(self)

    @staticmethod
    def deserialize(data):
        return BiiType(data)
