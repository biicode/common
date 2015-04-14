'''
Bson encode and decode
'''

from bson import BSON


def decode_bson(data):
    return BSON.decode(BSON(data))


def encode_bson(data):
    return BSON.encode(data)
