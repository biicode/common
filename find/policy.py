from biicode.common.utils.serializer import serialize, ListDeserializer
from collections import namedtuple
from biicode.common.edition.parsing.conf.conf_file_parser import parse
from biicode.common.exception import BiiException
from biicode.common.model.version_tag import VersionTag
import fnmatch


class Rule(namedtuple("Rule", ["block", "tag"])):
    """ each Rule is a block pattern and a minimum accepted tag
    """

    @staticmethod
    def deserialize(data):
        return Rule(data[0], data[1])

    def evaluate_block(self, brlblock):
        """ tells if the current block matches this pattern
        """
        return fnmatch.fnmatch(brlblock.to_pretty(), self.block)

    def evaluate(self, block_version, tag):
        """ both the block and the tag must satisfy the rule.
        return None if no block match, othewise Bool depending on tag
        """
        '''return None if the rule doesn't match, the priority otherwise'''
        matched = self.evaluate_block(block_version.block)
        if not matched:
            return None
        if self.tag <= tag:
            return True
        return False


default_policies = '''# This file configures your finds of dependencies.
#
# It is an ordered list of rules, which will be evaluated in order, of the form:
#     block_pattern: TAG
#
# For each possible block that could resolve your dependencies,
# only versions with tag >= TAG will be accepted

YOUR_USER_NAME/* : DEV
* : STABLE

'''


class Policy(list):
    """ A list of policy Rules to be matched to accept a version as solution for
    find
    """
    @classmethod
    def loads(cls, text):
        """ gets a Policy from a text string
        """
        result = cls()

        def policies_line_parser(line):
            try:
                pattern, path = line.split(":")
                pattern = pattern.strip()
                tag = VersionTag.loads(path.strip())
                result.append(Rule(pattern, tag))
            except:
                raise BiiException("Incorrect rule in policies.bii: %s" % line)

        parse(text, policies_line_parser, 0)
        if not result:
            raise BiiException("Empty policies.bii, cannot find")
        return result

    def filter(self, block_brls):
        '''from a set of BRLBlocks, return those that match some policy'''
        result = set()
        for block in block_brls:
            for rule in self:
                if rule.evaluate_block(block):
                    result.add(block)
                    break
        return result

    def evaluate(self, block_version, tag):
        '''return True if accepted, False otherwise'''
        for rule in self:
            accepted = rule.evaluate(block_version, tag)
            if accepted is not None:
                return accepted
        return False

    def serialize(self):
        return serialize(list(self))  # remove type, then serialize

    @classmethod
    def deserialize(cls, data):
        aux = ListDeserializer(Rule).deserialize(data)
        result = Policy(aux)
        return result

    @classmethod
    def default(cls):
        return Policy.loads(default_policies)
