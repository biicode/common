from types import NoneType
import os


def default(value):
    return value


def default_int(value):
    return int(value)


def default_float(value):
    return float(value)


def default_list(value):
    return value.split(",")


def default_bool(value):
    return value == '1'


default_type = {str: default,
                NoneType: default,
                int: default_int,
                float: default_float,
                list: default_list,
                bool: default_bool}


def get_env(env_key, default=None, environment=os.environ):

    env_var = environment.get(env_key, default)
    if env_var != default:
        func = default_type[type(default)]
        env_var = func(env_var)
    return env_var
