import yaml


def yaml_loads(cls, text):
    y = yaml.load(text)
    return cls.deserialize_dict(y)


def yaml_dumps(item):
    s = item.serialize_dict()
    return yaml.dump(s)
    #return yaml.safe_dump(s, default_flow_style=False)
