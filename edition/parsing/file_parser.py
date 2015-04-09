import re
from biicode.common.edition.parsing.parser import BII_DATA_REF
from biicode.common.edition.parsing.code_reference import CodeReference, CPPItem
from biicode.common.utils.bii_logging import logger
from biicode.common.edition.parsing.conf.comments_tags_parser import parse_tags


class ParserItem(object):
    def __init__(self, type_, content, start, end):
        self.type = type_
        self.content = content
        self.start = start
        self.end = end

    def __repr__(self):
        result = []
        result.append('%s %d-%d %s' % (self.type, self.start, self.end,
                                       self.content.replace('\n', ' ')))
        return '\n'.join(result)


class FileParser(object):
    initial_pattern = re.compile(r'''//|#|'|"|/[*]''')
    closing_quotes_pattern = re.compile(r'"|\\')
    start_include_pattern = re.compile(r'"|<')
    statement_pattern = re.compile(r';|{')
    bracket_pattern = re.compile(r'{|}')

    TEXT = 'TEXT'
    COMMENT = 'COMMENT'
    MULTILINE = 'MULTILINE'
    PREPROCESSOR = 'PREPROCESSOR'
    limits = {'//': ('\n', COMMENT),
            '/*': ('*/', MULTILINE),
            '"': ('"', TEXT),
            "'": ("'", TEXT),
            '#': ('\n', PREPROCESSOR)}

    def parse(self, code):
        '''main entry point for parsing the text "code"
        return tuple(includes(list), references(list), declarations(set), definitions(set),
        tags(dict))'''
        #This 2 lines where in normalizing Blob. A final \n is required for some things to be
        #correctly parsed
        if not code.endswith('\n'):
            code = '%s\n' % code

        result, simple_code = self._parse_strings_comments(code)
        declarations, definitions = self._extract_symbols(simple_code)
        includes, references = self._parse_references(result)
        comments = self.parse_comments(result)
        tags = parse_tags(comments)           # parse all biicode tags, comments with "bii:#"
        return includes, references, declarations, definitions, tags

    @staticmethod
    def tokenize_code(code):
        tokens = re.split(r'(\W)', code)
        stat_tokens = []
        for token in tokens:
            token = token.strip()
            if token and token != '\n':
                stat_tokens.append(token)
        return stat_tokens  # [token for token in tokens if token]

    def find_directive_end(self, content, start):
        while True:
            fin = content.find('\n', start + 1)
            if fin == -1 or fin == start:
                return fin
            aux = content[start:fin].rstrip()  # check for multiline breaks
            if len(aux) == 0 or aux[-1] != '\\':
                return fin
            start = fin + 1

    def _parse_strings_comments(self, source):
        result = []
        code = []
        begin = 0
        end = len(source)

        while begin < end:
            m = self.initial_pattern.search(source, begin)
            if m:  # some was found
                start = m.start()
                opening = m.group()
                if begin != start:
                    code.append(source[begin:start])
                closing = self.limits[opening][0]
                type_ = self.limits[opening][1]
                size_closing = len(closing)
                if opening == '#':
                    fin = self.find_directive_end(source, start + 1)
                elif closing == '"':
                    fin = self.find_closing_quotes(source, start + 1)
                elif closing == "'":
                    fin = start + 2 if source[start + 1] != '\\' else start + 3
                else:
                    fin = source.find(closing, start + 1, end)
                if fin == -1:
                    logger.info('ERROR, closing character not found for %s at %s'
                                % (opening, m.start()))
                    break
                fin += size_closing
                result.append(ParserItem(type_, source[start:fin], start, fin))
                begin = fin
            else:
                code.append(source[begin:end])
                break

        return result, ''.join(code)

    def _extract_symbols(self, code):
        declarations = set()
        definitions = set()
        self.recursive_parser(code, '', declarations, definitions)
        return declarations, definitions

    def recursive_parser(self, code, scope, declarations, definitions):
        for statement in self.get_statements(code):
            self.handle_statement(statement, scope, declarations, definitions)

    def get_statements(self, code):
        begin = 0
        end = len(code)

        while begin < end:
            m = self.statement_pattern.search(code, begin)
            if not m:  # none was found
                break
            c = m.group()
            start = m.start()
            if c == ';':
                statement = (code[begin:start], None)
                begin = start + 1
            else:
                closing = self.find_closing_bracket(code, start + 1)
                if closing == -1:
                    closing = end
                statement = (code[begin:start], code[start + 1:closing])
                begin = closing + 1
            yield statement

    def find_closing_bracket(self, code, start):
        try:
            count = 0
            end = len(code)
            while start < end:
                m = self.bracket_pattern.search(code, start)
                if not m:  # none was found
                    break
                c = m.group()
                if c == '{':
                    count += 1
                else:
                    count -= 1
                if count < 0:
                    return m.start()
                start = m.start() + 1
        except:
            pass
        return -1

    def handle_statement(self, statement, scope, declarations, definitions):
        tokens = self.tokenize_code(statement[0])
        if not tokens:
            return

        if '(' in tokens:
            name, scop = self._extract_scope_and_name(tokens, '(')
            scope = CPPItem.extend_scope(scope, scop)
            if statement[1] is None:
                declarations.add(CPPItem(CPPItem.METHOD, name, scope))
            else:
                definitions.add(CPPItem(CPPItem.METHOD, name, scope))
            return

        if 'namespace' in tokens:
            if statement[1] is not None:
                try:
                    name = tokens[tokens.index('namespace') + 1]
                    scope = CPPItem.extend_scope(scope, name)
                    self.recursive_parser(statement[1], scope, declarations, definitions)
                except:
                    pass  # Anonimous namespace
            return

        if 'class' in tokens:
            if statement[1] is not None:
                class_index = -1
                # Inheritance case
                if ':' in tokens:
                    class_index = tokens.index(':') - 1
                name = tokens[class_index]  # If class or struct, the class name is the last one
                declarations.add(CPPItem(CPPItem.CLASS, name, scope))
            return

        if 'struct' in tokens and statement[1] is not None and tokens[-1] != '=':
            name = tokens[-1]  # If class or struct, the class name is the last one
            declarations.add(CPPItem(CPPItem.STRUCT, name, scope))
            return

        if 'using' in tokens:
            return

        if 'extern' in tokens and statement[1] is not None:  # for extern "C" { constructs
            self.recursive_parser(statement[1], scope, declarations, definitions)

        if '[' in tokens:  # declaring array
            name, scop = self._extract_scope_and_name(tokens, '[')
            scope = CPPItem.extend_scope(scope, scop)
        elif '=' in tokens:
            name, scop = self._extract_scope_and_name(tokens, '=')
            scope = CPPItem.extend_scope(scope, scop)
        else:
            name, scop = self._extract_scope_and_name(tokens)
            scope = CPPItem.extend_scope(scope, scop)

        if 'extern' in tokens:
            declarations.add(CPPItem(CPPItem.VAR, name, scope))
            return
        definitions.add(CPPItem(CPPItem.VAR, name, scope))

    def _parse_references(self, result):
        includes = []
        references = []
        for item in result:
            if item.type == self.PREPROCESSOR:
                begin, end, include = self.handle_preprocessor(item.content)
                if include:
                    includes.append(CodeReference(include, item.start + begin, item.start + end))
            elif item.type == self.COMMENT or item.type == self.MULTILINE:
                data = self.handle_comment(item.content)
                if data:
                    # +2, -1 to account for // and line ending
                    references.append(CodeReference(data, item.start + len(BII_DATA_REF) + 2,
                                                    item.end - 1))
        return includes, references

    def parse_comments(self, result):
        """Returns an ordered list of COMMENTS
        """
        comments = []
        for item in result:
            if item.type == self.COMMENT or item.type == self.MULTILINE:
                comments.append(item.content)
        return comments

    def find_closing_quotes(self, text, start):
        while start < len(text):
            m = self.closing_quotes_pattern.search(text, start)
            if not m:  # none was found
                break
            c = m.group()
            pos = m.start()
            if c == '"':
                return pos
            start = pos + 2
        return -1

    def _extract_scope_and_name(self, tokens, symbol=None):
        """Extract declaration name and scope.
            Arguments
            --------
                tokens: string list()
                symbol: str - If we're looking for a method declaration symbol will be '('
                        to find declaration name.

            :return name, scope - list()
        """
        # When symbol is none index raises an exception.
        # This case is covered because int x; is one of this cases

        try:
            name_index = tokens.index(symbol) - 1
        except ValueError:
            name_index = len(tokens) - 1
        name = tokens[name_index]
        if tokens[name_index - 1] == '~':  # To handle destructor case
            name = '~' + name
            name_index -= 1
        start = name_index
        while start > 2 and tokens[start - 1] == ':' and tokens[start - 2] == ':':
            start -= 3
        scope = ''.join(tokens[start:max(0, name_index - 2)])
        return name, scope

    def handle_preprocessor(self, text):
        closer = {'"': '"', '<': '>'}
        tokens = self.tokenize_code(text)
        if len(tokens) > 1 and tokens[1] in ('include', 'import'):
            # TODO: Do not tokenize the full preprocessor directive
            try:
                m = self.start_include_pattern.search(text)
                start = m.start() + 1
                c = closer[m.group()]
                end = text.find(c, start + 1)
                return start, end, text[start:end].strip()
            except:
                logger.error('Unable to parse include %s ' % text)
        return None, None, None

    def handle_comment(self, text):
        marker = text.find(BII_DATA_REF)
        if marker > 0:
            try:
                tokens = text[marker + len(BII_DATA_REF):].split()
                return tokens[0]
            except:
                pass
