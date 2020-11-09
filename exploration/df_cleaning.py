from ebuy.data_collection.misc import read_yaml
from ebuy.exploration.image_labeling import features
import os
import pandas as pd

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
img_path = config['download_path']
label_path = img_path + 'labels.csv'


def get_df_labels():
    return pd.read_csv(label_path, index_col=0, dtype={'features': str}).reset_index(drop=True)


def expand_feature_string(df):
    for i, feature in enumerate(features):
        df[feature] = df.features.str[i].astype(int)
    del df["features"]
    return df


def feature_group(df):
    def trunc_img_name(text):
        return text[:text.find('_')]

    df['item'] = df.apply(lambda row: trunc_img_name(row['img_name']), axis=1)
    grouped_df = df.groupby(by='item').max()
    return grouped_df


def img_df_feature_prep(df):
    df = expand_feature_string(df)
    df = feature_group(df)
    return df


def filter_multi_discs(df):
    return df[df['Multiple Discs'] == 0].copy()


def filter_multi_cases(df):
    return df[df['Multiple Cases'] == 0].copy()


def filter_irrelevant(df):
    return df[
        ~((df['Disc'] == 0) & (df['Case'] == 0) & (df['Manual'] == 0))
    ].copy()


def filter_img_df(img_df, option=('all', )):
    """Main filtering method that, optionally, calls smaller focused filters.
    Takes in image dataframe and option parameter.
    Options include: 'all' (default), 'cases', 'discs', 'irr', or
    you can combine options. Pass in option as a tuple of strings for multiple."""
    df = img_df.copy()

    if type(option) == str:
        option = (option, )
    option = tuple([opt for opt in option])
    option = tuple(map(lambda x: x.lower(), option))

    if 'cases' or 'all' in option:
        df = filter_multi_cases(df)
    if 'discs' or 'all' in option:
        df = filter_multi_cases(df)
    if 'irr' or 'all' in option:
        df = filter_irrelevant(df)
    return df


if __name__ == '__main__':
    label_df = get_df_labels()
    label_df = img_df_feature_prep(label_df)
    print(label_df.shape)
    label_df = filter_img_df(label_df)
    print(label_df.shape)
