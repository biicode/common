from biicode.common.edition.processors.deps_conf_file import parse_deps_conf
from biicode.common.edition.parsing.conf.main_conf_file_parser import parse_mains_conf
from biicode.common.model.symbolic.block_version_table import BlockVersionTable
import re
from biicode.common.edition.parsing.conf.parent import parent_loads
from collections import namedtuple
from biicode.common.edition.parsing.conf.conf_file_parser import parse
from biicode.common.exception import BiiException, ConfigurationFileError


template = r"""# Biicode configuration file

[requirements]
    # Blocks and versions this block depends on e.g.
    # user/depblock1: 3
    # user2/depblock2(track) @tag

[parent]
    # The parent version of this block. Must match folder name. E.g.
    # user/block  # No version number means not published yet
    # You can change it to publish to a different track, and change version, e.g.
    # user/block(track): 7

[paths]
    # Local directories to look for headers (within block)
    # /
    # include

[dependencies]
    # Manual adjust file implicit dependencies, add (+), remove (-), or overwrite (=)
    # hello.h + hello_imp.cpp hello_imp2.cpp
    # *.h + *.cpp

[mains]
    # Manual adjust of files that define an executable
    # !main.cpp  # Do not build executable from this file
    # main2.cpp # Build it (it doesnt have a main() function, but maybe it includes it)

[tests]
    # Manual adjust of files that define a CTest test
    # test/* pattern to evaluate this test/ folder sources like tests

[hooks]
    # These are defined equal to [dependencies],files names matching bii*stage*hook.py
    # will be launched as python scripts at stage = {post_process, clean}
    # CMakeLists.txt + bii/my_post_process1_hook.py bii_clean_hook.py

[includes]
    # Mapping of include patterns to external blocks
    # hello*.h: user3/depblock  # includes will be processed as user3/depblock/hello*.h

[cpp-std]
    # Add c++11, c++14, etc flags to any target (by default, BII_LIB_TARGET)
    # c++11 NO_REQUIRED PRIVATE
    # c++14 TARGET phil_superblock_main

[data]
    # Manually define data files dependencies, that will be copied to bin for execution
    # By default they are copied to bin/user/block/... which should be taken into account
    # when loading from disk such data
    # image.cpp + image.jpg  # code should write open("user/block/image.jpg")

"""

IncludeMap = namedtuple("IncludeMap", "pattern path")


class IncludesMapping(list):
    """ List of IncludeMaps
    """

    @classmethod
    def loads(cls, text, line):
        result = cls()

        def path_line_parser(line):
            try:
                pattern, path = line.split(":")
                pattern = pattern.strip()
                path = path.strip().rstrip("/")
                result.append(IncludeMap(pattern, path))
            except:
                raise BiiException("Incorrect include map: %s" % line)

        parse(text, path_line_parser, line)
        return result


class BiiConfig(object):
    sections = ['parent', 'requirements', 'paths', 'data', 'hooks', 'dependencies', 'includes',
                'mains', 'tests', 'cpp-std']

    def __init__(self, text):
        """ Create memory representation (parsing) of biicode block configuration file
        param block_name: (BlockName) the block name this conf file lives in
        param text: (str) the configuration text (normalized to LF only)
        """
        self._template = text is None
        self._text = text if text is not None else template
        assert '\r' not in self._text
        # Configuration fields
        self.parent = None
        self.requirements = BlockVersionTable()
        self.dependencies = []
        self.paths = []
        self.mains = []  # Can be sets
        self.includes = []
        self.data = []  # Can be sets
        self.tests = []
        self.cpp_std = []

        self._parse()

    def changed(self, other):
        """ check if something different to parent, changed between 2 config files.
        Necessary to discard changing parent as the only change in a block, e.g.
        while checking empty (no-changes) publications
        """
        return (self.requirements != other.requirements or
                self.mains != other.mains or
                self.paths != other.paths or
                self.dependencies != other.dependencies or
                self.data != other.data or
                self.includes != other.includes or
                self.tests != other.tests)

    def _find_sections(self):
        pattern = re.compile("^\[([a-z]{1,25}-?[a-z]{1,25})\]")
        current_lines = []
        sections = {}
        Section = namedtuple("Section", "line content headline")
        parsed_sections = set()
        for i, line in enumerate(self._text.splitlines()):
            m = pattern.match(line)
            if m:
                group = m.group(1)
                if group not in BiiConfig.sections:
                    raise ConfigurationFileError("%d: Unrecognized section '%s'" % (i + 1, group))
                if group in parsed_sections:
                    raise ConfigurationFileError("%d: Duplicated section '%s'" % (i + 1, group))
                parsed_sections.add(group)
                current_lines = []
                sections[group] = Section(i + 1, current_lines, line)
            else:
                current_lines.append(line)

        return {name: Section(line, '\n'.join(lines), headline)
                for name, (line, lines, headline) in sections.iteritems()}

    def _parse(self):
        sections = self._find_sections()

        parent = sections.get('parent')
        if parent:
            self.parent = parent_loads(parent.content, parent.line)
        self._old_parent = self.parent

        reqs = sections.get('requirements')
        if reqs:
            self.requirements = BlockVersionTable.loads(reqs.content, reqs.line)
        self._old_requirements = self.requirements.copy()

        # self.include_mapping = IncludesMapping.loads(includes)
        deps = sections.get('dependencies')
        if deps:
            self.dependencies = parse_deps_conf(deps.content, deps.line)

        hooks = sections.get('hooks')
        if hooks:
            hooks_deps = parse_deps_conf(hooks.content, hooks.line)
            self.dependencies.extend(hooks_deps)

        mains = sections.get('mains')
        if mains:
            self.mains = parse_mains_conf(mains.content, mains.line)

        tests = sections.get('tests')
        if tests:
            def test_line_parser(line):
                self.tests.append(line)
            parse(tests.content, test_line_parser, tests.line)

        paths = sections.get('paths')
        if paths:
            def path_line_parser(line):
                self.paths.append(line)
            parse(paths.content, path_line_parser, paths.line)

        data = sections.get('data')
        if data:
            self.data = parse_deps_conf(data.content, data.line)

        includes = sections.get('includes')
        if includes:
            self.includes = IncludesMapping.loads(includes.content, includes.line)

        cpp_std = sections.get('cpp-std')
        if cpp_std:
            def cpp_std_line_parser(line):
                self.cpp_std.append(line)
            parse(cpp_std.content, cpp_std_line_parser, cpp_std.line)

    def _dump_requirements(self, sections):
        if self.requirements != self._old_requirements:
            assert all(v.time is not None for v in self.requirements.itervalues())
            new_reqs = ["\t %s" % v.to_pretty() for v in sorted(self.requirements.itervalues())]
            old_reqs = sections.get("requirements")
            if old_reqs:
                new_content = "%s\n%s\n" % (old_reqs.headline, '\n'.join(new_reqs))
                old_content = "%s\n%s" % (old_reqs.headline, old_reqs.content)
                self._text = self._text.replace(old_content, new_content)
            else:
                self._text = self._text + "\n[requirements]\n" + '\n'.join(new_reqs)
            self._old_requirements = self.requirements.copy()
            assert isinstance(self._old_requirements, BlockVersionTable)
            return True

    def _dump_parent(self, sections):
        if self.parent != self._old_parent:
            new_parent = "\t" + self.parent.to_pretty()
            old = sections.get("parent")
            if old:
                new_content = "%s\n%s" % (old.headline, new_parent)
                old_content = "%s\n%s" % (old.headline, old.content)
                self._text = self._text.replace(old_content, new_content)
            else:
                self._text = self._text + "\n[parent]\n" + new_parent
            self._old_parent = self.parent
            return True

    def dumps(self):
        """
        return modified text (str) of configuration file or None if it didnt change
        """
        sections = self._find_sections()
        req_mod = self._dump_requirements(sections)
        par_mod = self._dump_parent(sections)
        if req_mod or par_mod or self._template:
            self._template = False
            return self._text
