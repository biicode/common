import cPickle as pickle
BII_DATA_REF = r"bii://"        # indicates a biicode data reference


class Parser(object):

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        if data is None:
            return None
        #FIXME: Correctly serialize
        utf8 = data.encode(encoding='UTF-8')
        parser = pickle.loads(utf8)
        return parser
