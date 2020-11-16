import os

from data_readiness.read_db import get_dfs
from data_readiness.label_df_cleaning import join_to_main_df as img_join
from data_readiness.text_preprocess import nlp_join, get_nlp_df
from data_collection.misc import read_yaml

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
csv_path = config['csv_path']
data_path = csv_path + 'train.csv'

if not os.path.exists(csv_path):
    os.mkdir(csv_path)
    print(f'Made path! {csv_path}')

# Allow price thresholding
price_range = (20, 100)

# Read in data from PSQL
df, _, _ = get_dfs()

# Collect NLP data with above method.
nlp_df = get_nlp_df(df)


def df_filtering(df, prices, img_opts='all', nlp=True, **kwargs):
    """Method that filters out main dataframe based
    on image criteria and joins img/nlp dataframes.
    Args:
        df: pd.DataFrame
        prices: (int, int) for a price range filter
        img_opts: (str, ..., str) or str passed to
            img_join()
        nlp: bool controlling nlp_join()
        **kwargs: Other parameters to pass to img_join()
    Returns:
        pd.DataFrame"""
    min_price, max_price = prices
    if img_opts:
        df = img_join(df, img_opts, **kwargs)
    if nlp:
        df = nlp_join(df, nlp_df)
    df = df[(df.price > min_price) & (df.price <= max_price)]
    return df


if __name__ == '__main__':
    df = df_filtering(df, price_range)
    df.to_csv(data_path)
