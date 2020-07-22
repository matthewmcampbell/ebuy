import yaml


def read_yaml(path):
    with open(path, 'r') as conf:
        try:
            res = yaml.safe_load(conf)
        except yaml.YAMLError as exc:
            print(exc)
            res = {}
    return res