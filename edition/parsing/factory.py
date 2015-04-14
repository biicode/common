from biicode.common.edition.parsing.cpp.drl_parser import DRLCPPParser
from biicode.common.edition.parsing.python.py_parser import PythonParser
from biicode.common.edition.parsing.nodejs.js_parser import NodeJSParser
from biicode.common.edition.parsing.nodejs.json_parser import PackageJSONParser
from biicode.common.edition.parsing.fortran.fortran_parser import FortranParser
from biicode.common.model.bii_type import CPP, PYTHON, JS, FORTRAN, CMAKE
from biicode.common.edition.parsing.cmake.cmake_parser import CMakeParser

PARSERS = {CPP: DRLCPPParser,
           PYTHON: PythonParser,
           JS: NodeJSParser,
           FORTRAN: FortranParser,
           CMAKE: CMakeParser}

PARSEABLE_FILE = {"package.json": PackageJSONParser}


def parser_factory(biitype, filename):
    """Return parser depending on type and also on filename constraints."""
    parser = PARSEABLE_FILE.get(filename, PARSERS.get(biitype))
    if parser:
        return parser()
