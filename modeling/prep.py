from data_collection.misc import read_yaml
import os
import pandas as pd

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
csv_path = config['csv_path']
data_path = csv_path + 'train.csv'


def read_data(data_path=data_path):
    """Method that reads in csv data at path determined in config.yaml.
    If no file is present, will throw an error. Need to run main.py
    in cleaning folder to make csv."""
    try:
        df = pd.read_csv(data_path, index_col=0)
    except FileNotFoundError:
        print("""No data file detected! 
        Try running the main script in "cleaning""""")
        exit(1)
    return df


def handle_missing(df):
    """Method to handle all missing values on a
    per column basis. See data_handling_notes.txt
    for all reasonings on these methods.

    Args:
        df: pd.DataFrame generated from read_data()

    Returns:
        df: pd.DataFrame"""
    def _drop_cols(df):
        cols = ['id', 'bundle', 'text', 'bid_summary']
        return df.drop(columns=cols)

    def _cond(df):
        return pd.get_dummies(df, columns=['cond'])

    def _seller_percent(df):
        df.seller_percent = df.seller_percent.fillna(
            df.seller_percent.median()
        )
        return df

    def _rating_count(df):
        df.rating_count = df.rating_count.fillna(
            df.rating_count.median()
        ).astype('category')
        return df

    def _bid_duration(df):
        df = df[df.bid_duration.str.contains('day')].copy()
        df_dummy = pd.get_dummies(df, columns=['bid_duration'])
        return df_dummy

    def _img_features(df):
        cols = ['Disc', 'Disc (Under)', 'Case', 'Manual', 'Screen',
                    'Multiple Discs', 'Multiple Cases']
        df['Missing_img'] = df['Disc'].isna().astype('int').astype('category')
        df[cols] = df[cols].fillna(0).astype('category')
        return df

    initial_rows = df.shape[0]
    nans_removed = (df.pipe(_drop_cols)
                      .pipe(_cond)
                      .pipe(_seller_percent)
                      .pipe(_rating_count)
                      .pipe(_bid_duration)
                      .pipe(_img_features))

    after_rows = nans_removed.shape[0]
    loss = round((initial_rows - after_rows) / initial_rows, 2)
    print(f"""Started with {initial_rows} rows.\n
Ended with {after_rows}.\n
Lost approx {loss}""")
    return nans_removed.reset_index(drop=True)
