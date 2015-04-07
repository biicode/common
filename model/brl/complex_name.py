import re
from biicode.common.exception import InvalidNameException


class ComplexName(str):
    """Complex biicode name

    Stores a name for every group_name.name (block name) and branch names
    Valid names MUST begin with a letter or number, and contain
    a min of 3 chars and max of 20 characters, including:
    letters, numbers, underscore, dot and dash
    """
    max_chars = 20
    min_chars = 2
    base_er = "[a-zA-Z0-9_]+[a-zA-Z0-9_\.-]{%s,%s}" % (min_chars - 1, max_chars)
    regular_expression = "^%s$" % base_er
    pattern = re.compile(regular_expression)

    def __new__(cls, name, validate=True):
        """Simple name creation.

        @param name:        string containing the desired name
        @param validate:    checks for valid complex name. default True
        """
        if validate:
            name = ComplexName.validate(name)
        return str.__new__(cls, name)

    @staticmethod
    def validate(name):
        """Check for name compliance with pattern rules"""
        try:
            if ComplexName.pattern.match(name) is None:
                if len(name) > ComplexName.max_chars:
                    message = "'%s' is too long. Valid names must " \
                              "contain at most %s characters." % (name, ComplexName.max_chars)
                elif len(name) < ComplexName.min_chars:
                    message = "'%s' is too short. Valid names must contain"\
                              " at least %s characters." % (name, ComplexName.min_chars)
                else:
                    message = "'%s' is an invalid name. Valid names MUST begin with a "\
                                "letter or number, have between %s-%s chars, including "\
                                "letters, numbers, underscore,"\
                                " dot and dash" % (name, ComplexName.min_chars,
                                                   ComplexName.max_chars)
                raise InvalidNameException(message)
            return name
        except AttributeError:
            raise InvalidNameException('Empty name provided', None)
