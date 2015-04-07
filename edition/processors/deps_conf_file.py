from collections import namedtuple
from biicode.common.exception import ConfigurationFileError
from biicode.common.edition.parsing.conf.conf_file_parser import parse


def parse_deps_conf(text, line_number):
    dependencies = []

    def parse_dependencies(line):
        dep = DependentConfiguration.parse(line)
        dependencies.append(dep)

    parse(text,  parse_dependencies, line_number)
    return dependencies


class DependencyConfiguration(namedtuple('DependencyConfiguration', ['exclude', 'name'])):
    """Represent a single target dependency from dependencies.bii file."""
    EXCLUDE_FLAG = '!'

    @classmethod
    def parse(cls, dep):
        exclude = dep[0] == cls.EXCLUDE_FLAG
        if exclude:
            name = dep[1:]
        else:
            name = dep
        obj = cls(exclude, name)
        return obj

    def __repr__(self):
        return '%s%s' % ('!' if self.exclude else '', self.name)


class DependentConfiguration(namedtuple('DependentConfiguration',
                                        ['pattern', 'action', 'dependencies'])):
    '''Stores the info from one line of the dependencies.bii file'''
    ADD_FLAG = '+'
    REMOVE_FLAG = '-'
    ASSIGN_FLAG = '='

    @classmethod
    def parse(cls, line):
        tokens = line.strip().split()
        if len(tokens) < 2:
            raise ConfigurationFileError('line is missing elements')
        pattern = tokens[0]
        action = tokens[1]
        if action not in ('+-='):
            action = pattern[0]
            if action not in ('+-='):
                action = '+'
            else:
                pattern = pattern[1:]
            deps = tokens[1:]
        else:
            deps = tokens[2:]

        dependencies = set()
        for token in deps:
            if token == 'NULL':
                break
            dependencies.add(DependencyConfiguration.parse(token))
        obj = cls(pattern, action, dependencies)
        return obj

    def update_dependencies(self, implicit_deps, dependencies):
        if self.action == self.ASSIGN_FLAG:
            implicit_deps.clear()
        for dep in dependencies:
            if self.action == self.REMOVE_FLAG:
                implicit_deps.discard(dep)
            else:
                implicit_deps.add(dep)

    def __repr__(self):
        return '%s %s %s' % (self.pattern, self.action,
                             ' '.join(repr(d) for d in self.dependencies))
