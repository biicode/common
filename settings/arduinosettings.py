from biicode.common.settings.smart_serial import smart_serialize, smart_deserialize
from biicode.common.exception import ConfigurationFileError
from biicode.common.settings.loader import yaml_dumps
import os


Arduino_programmers = ["avrisp", "avrispmkii", "usbtinyisp", "usbasp", "parallel", "arduinoisp"]


class ArduinoSettings(object):
    """
        Attributes
        ----------
            board: board
                Store information about the board type.
            port: port
                Store information about the USB port.
            programmer: programmer
                Store information about the programmer type.
            automatic_reset: True or False
                When board port need to be reseted automatically"""

    smart_serial = {'board': ('board', None, None),
                    'port': ('port', None, None),
                    'programmer': ('programmer', None, None),
                    'sdk': ('sdk', None, None),
                    'version': ('version', None, None),
                    'generator': ('generator', None, None),
                    'automatic_reset': ('automatic_reset', None, None)}

    def __init__(self):
        self.board = None
        self.port = None
        self.programmer = "usbtinyisp"
        self.sdk = None
        self.version = None
        self.generator = None
        self.automatic_reset = None

    def __nonzero__(self):
        if self.board or self.port:
            return True
        return False

    def __eq__(self, other):
        return self.board == other.board and \
               self.port == other.port and self.programmer == other.programmer and \
               self.sdk == other.sdk and self.version == other.version and \
               self.generator == other.generator and self.automatic_reset == other.automatic_reset

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return yaml_dumps(self)

    def serialize(self):
        serial = smart_serialize(self)
        return serial

    @classmethod
    def deserialize(cls, data):
        try:
            d = smart_deserialize(cls, data)
        except ValueError as error:
            raise ConfigurationFileError("Error parsing settings.bii %s %s" % (os.linesep, error))
        return d

    serialize_dict = serialize
    deserialize_dict = deserialize
