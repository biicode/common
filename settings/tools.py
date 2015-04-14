from biicode.common.settings.fixed_string import FixedString
from biicode.common.settings.tool_info import ToolInfo
import copy


class Architecture(FixedString):
    """ Known architectures
    """
    values = {'AMD64', 'X86_64', 'IA64', 'X86', '64bit', '32bit', 'Win64', 'ARM', 'AVR'}


class Language(FixedString):
    """ Known programming languages
    """
    values = ['node', 'fortran', 'python', 'cpp', 'arduino']


class CompilerFamily(FixedString):
    """ Known compilers
    """
    values = {'gnu', 'vc', 'gfortran', 'arduinosdk'}


class CompilerSubFamily(FixedString):
    values = {'mingw'}


class Compiler(ToolInfo):
    smart_serial = copy.copy(ToolInfo.smart_serial)
    smart_serial['family'] = ('family', CompilerFamily, None)
    smart_serial['subfamily'] = ('subfamily', CompilerSubFamily, None)
    smart_serial['arch'] = ('arch', Architecture, None)

    def __init__(self, family=None, subfamily=None, version=None, code=None, arch=None):
        if subfamily:
            subfamily = CompilerSubFamily(subfamily)
        ToolInfo.__init__(self, CompilerFamily(family), subfamily, version, code, arch)


class RunnerFamily(FixedString):
    values = {'node', 'python'}


class Runner(ToolInfo):
    smart_serial = copy.copy(ToolInfo.smart_serial)
    smart_serial['family'] = ('family', RunnerFamily, None)

    def __init__(self, family=None, subfamily=None, version=None, code=None, arch=None):
        ToolInfo.__init__(self, RunnerFamily(family), subfamily, version, code, arch)


class BuilderFamily(FixedString):
    values = {'msbuild', 'make', 'nmake', 'ant', 'maven'}


class Builder(ToolInfo):
    smart_serial = copy.copy(ToolInfo.smart_serial)
    smart_serial['family'] = ('family', BuilderFamily, None)

    def __init__(self, family=None, subfamily=None, version=None, code=None, arch=None):
        ToolInfo.__init__(self, BuilderFamily(family), subfamily, version, code, arch)
