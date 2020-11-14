import yaml

from functools import wraps


def read_yaml(path: str) -> dict:
    """Method to read yaml file into dict easily.
    Args:
        path: str to yaml file
    Returns:
        dict"""
    with open(path, 'r') as conf:
        try:
            res = yaml.safe_load(conf)
        except yaml.YAMLError as exc:
            print(exc)
            res = {}
    return res


def return_on_fail(default, error=Exception):
    """Wrapper method to return a specified default
    value when an error occurs. This is useful since
    the webscraper can display inconsistent behavior
    over time.
    Args:
        default: Anything writable to pd.DataFrame
        error: The error you are guarding against.
    Returns:
        f: modified function"""
    def outer_wrapper(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except error as e:
                print(f'Error on function: {func} \t {e}')
                return default
        return new_func
    return outer_wrapper
