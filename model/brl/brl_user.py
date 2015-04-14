from biicode.common.exception import InvalidNameException
import re


class BRLUser(str):
    """Biicode Resurce Locator for a user
    """

    base_er = "[a-zA-Z][a-zA-Z0-9_]{1,49}"
    pattern = re.compile("^%s$" % base_er)

    def create_block_name(self, name):
        from block_name import BlockName
        return BlockName('%s/%s' % (self, BRLUser(name)))

    def __new__(cls, name, validate=True):
        """Simple name creation.

        @param name:        string containing the desired name
        @param validate:    checks for valid simple name. default True
        """
        if validate:
            name = BRLUser.validate(name)
        return str.__new__(cls, name)

    @staticmethod
    def validate(name):
        """Check for name compliance with pattern rules. User names can be
           with upper/lower case
        """
        try:
            name = name.strip()
            if BRLUser.pattern.match(name) is None:
                if len(name) > 49:
                    message = "'%s' is too long. Valid names must contain at most 50 characters."
                elif len(name) < 2:
                    message = "'%s' is too short. Valid names must contain at least 2 characters."
                else:
                    message = "'%s' is an invalid name. "\
                              "Valid names should begin with alphanumerical characters."
                raise InvalidNameException(message % name)
            return name
        except AttributeError:
            raise InvalidNameException('Empty name provided', None)
