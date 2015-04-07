from biicode.common.settings.tools import Compiler, Builder, Runner
from biicode.common.settings.loader import yaml_dumps


class LanguageSettings(object):
    """Generic class to store specific information needed to run a project written in that language.

        Attributes
        ----------
            compiler: Compiler
                Store information about project compiler.
            builder: Builder
                Store information about project builder.
            runner: Runner
                Store information about project runner.
            ide: IDE
                Store information about used IDE.

    """

    def __init__(self):
        self.compiler = Compiler()
        self.builder = Builder()
        self.runner = Runner()

    def __nonzero__(self):
        if self.compiler or self.builder or self.runner:
            return True
        return False

    def __eq__(self, other):
        if self is other:
            return True
        return isinstance(other, self.__class__) \
            and self.compiler == other.compiler \
            and self.builder == other.builder \
            and self.runner == other.runner

    def __ne__(self, other):
        return not self.__eq__(other)

    smart_serial = {'compiler': ('compiler', Compiler, Compiler),
                    'builder': ('builder', Builder, Builder),
                    'runner': ('runner', Runner, Runner)}

    def __repr__(self):
        return yaml_dumps(self)
