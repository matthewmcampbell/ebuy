from data_collection.misc import read_yaml
import os
import pandas as pd

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
csv_path = config['csv_path']
data_path = csv_path + 'train.csv'


def read_data():
    try:
        df = pd.read_csv(data_path, index_col=0)
    except FileNotFoundError:
        print("""No data file detected! 
        Try running the main script in "cleaning""""")
        exit(1)
    return df


df = read_data()
df.notnull().all().to_csv('check.csv')


def handle_missing(df):

    def handle_bundle():
        df.fillna()