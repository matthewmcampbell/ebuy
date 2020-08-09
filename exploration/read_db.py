import pandas as pd
import os
from data_collection.misc import read_yaml
from data_collection.req_to_db import psql_connect


folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'data_collection', 'conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', 'data_collection', config['secrets']))


def psql_to_pandas(query=''):
    return pd.read_sql(query, psql_connect(config, secrets))


df = psql_to_pandas('SELECT count(id) from main;')
