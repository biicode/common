from biicode.common.utils.serializer import Serializer
from biicode.common.utils.bii_logging import logger


def smart_serialize(obj):
    args = []
    for field, (key, _, _) in obj.smart_serial.iteritems():
        a = getattr(obj, field)
        #TODO: Check field exist
        if a:
            args.append((key, a))
    ret = Serializer().build(*args)
    return ret


def smart_deserialize(cls, data):
    '''KNOWN PROBLEM: this deserializer simply ignores data fields not
    represented in the smart_serial map, without any warning or user info.
    In such way it is robust to changes, but for example an error in Settings
    as writing compilr: instead of compiler: are not detected, simply ignored'''
    t = cls()
    for field, (key, cls1, cls2) in cls.smart_serial.iteritems():
        d = data.get(key)
        if d:
            if cls1:
                d = cls1.deserialize(d)
        else:
            if cls2:
                d = cls2()
        setattr(t, field, d)
    for field in data.keys():
        if field not in cls.smart_serial:
            logger.error('Error in %s: %s' % (cls.__name__, field))
    return t
