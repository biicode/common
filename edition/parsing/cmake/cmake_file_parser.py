'''
CMake file parser. CMake language is case insensitive.

Methods to parse:
    INCLUDE()
    ADD_SUBDIRECTORY()
    CONFIGURE_FILE()
'''
from biicode.common.edition.parsing.file_parser import FileParser
import re
from biicode.common.edition.parsing.code_reference import CodeReference


class CMakeFileParser(FileParser):
    ''' Class to parse a text CMake code '''

    comments_pattern = re.compile(r'''\s*\#(.+?)\n''')

    # INCLUDE, ADD_SUBDIRECTORY and CONFIGURE_FILE are case insensitive
    global_pattern = r'(?:\s*%s\s*)\((.+?)\)'
    include_pattern = re.compile(global_pattern % 'include', re.IGNORECASE | re.DOTALL)
    add_subdirectory_pattern = re.compile(global_pattern % 'add_subdirectory',
                                          re.IGNORECASE | re.DOTALL)
    configure_file_pattern = re.compile(global_pattern % 'configure_file',
                                        re.IGNORECASE | re.DOTALL)

    def parse(self, code):
        '''main entry point for parsing the text "code" return tuple(includes(list)'''
        #This 2 lines where in normalizing Blob. A final \n is required for some things to be
        #correctly parsed
        if not code.endswith('\n'):
            code = '%s\n' % code

        includes = self._get_file_includes(code)
        return includes

    def _get_file_includes(self, code):
        includes = []
        simple_code = self._get_simple_code(code)
        # INCLUDE()
        includes += self._parse_global_includes(simple_code, self.include_pattern,
                                                suitable_format='.cmake', is_folder=False)
        # ADD_SUBDIRECTORY()
        includes += self._parse_global_includes(simple_code, self.add_subdirectory_pattern,
                                                suitable_format=None, is_folder=True)
        # CONFIGURE_FILE()
        includes += self._parse_global_includes(simple_code, self.configure_file_pattern,
                                                suitable_format=None, is_folder=False)
        return includes

    def _get_simple_code(self, code):
        simple_code = []
        start = 0
        end = len(code)
        for comment_match in self.comments_pattern.finditer(code):
            _, comment_start, comment_end = self._get_parsed_group(comment_match, 0)
            if start != comment_start:
                simple_code.append(code[start:comment_start] + '\n')
            start = comment_end
        if start < end:
            simple_code.append(code[start:end])
        return ''.join(simple_code)

    def _parse_global_includes(self, simple_code, pattern, suitable_format=None, is_folder=False):
        includes = []
        for include_match in pattern.finditer(simple_code):
            include, include_start, include_end = self._get_parsed_group(include_match)
            _include = self._get_valid_include(include, suitable_format, is_folder)
            if _include:
                includes.append(CodeReference(_include,
                                              include_start,
                                              include_end))
        return includes

    def _get_parsed_group(self, matched_group, num_group=1):
        return matched_group.group(num_group), matched_group.start(num_group),\
               matched_group.end(num_group)

    def _get_valid_include(self, include, suitable_format=None, is_folder=False):
        ''' parameter:
              include:
                    ../block/configure       -> OK
                    "fenix/block/configure"  -> OK
                    'fenix/block/configure'  -> OK
                    fenix\\block\\configure  -> OK
                    fenix\block\configure    -> BAD
            return:
                    include with all the useless characters replaced
        '''
        include = include.strip()  # delete possibles whitespace
        include = include.split(' ')[0]  # if configure_file("input_dir" "output_dir")
        # By the moment CMake vars isn't parsed
        if '$' in include:
            return None
        include = include.replace('"', '').replace("'", '')
        include = include.replace('\\\\', '/')  # if Windows
        include = include.replace('\n', '')

        # If include is such ADD_SUBDIRECTORY(folder_include) or
        # if INCLUDE(MODULE/CMAKE/My_Macro) -> in this case '.cmake' is missing
        if suitable_format and not suitable_format in include and not is_folder:
            include = '%s%s' % (include, suitable_format)
        elif is_folder:
            include = '%s/CMakeLists.txt' % include
        return include
