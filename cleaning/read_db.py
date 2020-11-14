import pandas as pd
import os

from data_collection.misc import read_yaml
from data_collection.req_to_db import psql_connect


folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
secrets = read_yaml(os.path.join(folder, '..', config['secrets']))


def psql_to_pandas(query=''):
    """Method to read in generic query from PSQL DB.
    Args:
        query: str
    Returns:
        pd.DataFrame"""
    return pd.read_sql(query, psql_connect(config, secrets))


def get_dfs():
    """Method that reads the three tables from PSQL.
    Returns:
        (pd.DataFrame,) * 3"""
    df1 = psql_to_pandas('SELECT * FROM main;')
    df2 = psql_to_pandas('SELECT * FROM imgs;')
    df3 = psql_to_pandas('SELECT * FROM bids;')
    return df1, df2, df3
