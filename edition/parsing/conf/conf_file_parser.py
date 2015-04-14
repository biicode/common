from biicode.common.exception import ConfigurationFileError


def parse(text, line_parser, base_line_number=0):
    """Parse configuration file. parse_tokens method should be written on to provide behavior
    depending on each case.
    Comments with # and blank lines are skipped
    Params:
        text: string to be parsed on a per line basis
    """
    for i, line in enumerate(text.splitlines()):
        line = line.strip()
        if not line or line.startswith('#'):  # Blank and comment lines
            continue
        tokens = line.split('#', 1)
        line = tokens[0]
        if '<<<' in line or '===' in line or '>>>' in line:
            raise ConfigurationFileError('%d: merge conflict' % (i + 1 + base_line_number))

        try:
            line_parser(line)
        except Exception as e:
            raise ConfigurationFileError('%d: Parse error: \n\t%s'
                                         % (i + 1 + base_line_number, str(e)))
