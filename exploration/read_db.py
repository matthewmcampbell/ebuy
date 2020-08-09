import pandas as pd
import os
from ebuy.data_collection.misc import read_yaml
from ebuy.data_collection.req_to_db import psql_connect


folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', config['secrets']))


def psql_to_pandas(query=''):
    return pd.read_sql(query, psql_connect(config, secrets))


def get_dfs():
    df1 = psql_to_pandas('SELECT * FROM main;')
    df2 = psql_to_pandas('SELECT * FROM imgs;')
    df3 = psql_to_pandas('SELECT * FROM bids;')
    return df1, df2, df3
