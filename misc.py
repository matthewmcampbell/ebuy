import yaml
from functools import wraps


def read_yaml(path: str) -> dict:
    with open(path, 'r') as conf:
        try:
            res = yaml.safe_load(conf)
        except yaml.YAMLError as exc:
            print(exc)
            res = {}
    return res


def return_on_fail(default, error=Exception):
    def outer_wrapper(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except error:
                return default
        return new_func
    return outer_wrapper
