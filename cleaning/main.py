from cleaning.read_db import get_dfs
from cleaning.label_df_cleaning import join_to_main_df as img_join
from cleaning.text_preprocess import nlp_join, make_nlp_df
from data_collection.misc import read_yaml
import os


folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
csv_path = config['csv_path']
data_path = csv_path + 'train.csv'

if not os.path.exists(csv_path):
    os.mkdir(csv_path)
    print(f'Made path! {csv_path}')

# Allow price thresholding
min_price = 20
max_price = 100

# Read in data from PSQL
df, _, _ = get_dfs()


# Perform NLP formatting
def get_nlp_df(df):
    nlp_df = make_nlp_df(df)
    rename_cols = []
    for col in nlp_df.columns:
        if col in df.columns and col != 'id':
            rename_cols.append(col)
    rename_map = {col: col + '(w)' for col in rename_cols}
    return nlp_df.rename(columns=rename_map)


# Collect NLP data with above method.
nlp_df = get_nlp_df(df)


def df_filtering(df, prices, img_opts='all', nlp=True, **kwargs):
    min_price, max_price = prices
    if img_opts:
        df = img_join(df, img_opts, **kwargs)
    if nlp:
        df = nlp_join(df, nlp_df)
    df = df[(df.price > min_price) & (df.price <= max_price)]
    return df


# Filter out based on image filtering criteria
if __name__ == '__main__':
    df = df_filtering(df, (min_price, max_price))
    df.to_csv(data_path)
