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
        return text[:text.find('full')]

    df['item'] = df.apply(lambda row: trunc_img_name(row['img_name']), axis=1)
    grouped_df = df.groupby(by='item').max().reset_index()
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


def get_filtered_img_df(df, option=('all', )):
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


def filter_img_df(img_df, options):
    """Main filtering method that, optionally, calls smaller focused filters.
    Takes in image dataframe and option parameter.
    Options include: 'all' (default), 'cases', 'discs', 'irr', or
    you can combine options. Pass in option as a tuple of strings for multiple."""
    df = img_df.copy()
    df = get_filtered_img_df(df, options)
    return df


def filter_img_df_complement(img_df, options):
    """Similar to filter_img_df, but returns the filtered out rows instead."""
    df = img_df.copy()
    df = get_filtered_img_df(df, options)
    df_complement = img_df[~img_df.item.isin(df.item)]
    return df_complement


def image_label_filter(options, verbose=False):
    """Useful function to call full cleaning process after initial read in
    Args:
        options: (str,)
        Should be the same as options for filter_img_df

        verbose: bool
        Controls whether or not extra printing should occur.
        """
    label_df = get_df_labels()
    label_df = img_df_feature_prep(label_df)
    if verbose:
        print(f"Count of items before filtering: {label_df.shape[0]}")
    label_df = filter_img_df(label_df, options)
    if verbose:
        print(f"Count of items after filtering: {label_df.shape[0]}")
    return label_df


def image_label_filter_complement(options, verbose=False):
    """Useful function to call full cleaning process after initial read in
    Args:
        options: (str,)
        Should be the same as options for filter_img_df

        verbose: bool
        Controls whether or not extra printing should occur.
        """
    label_df = get_df_labels()
    label_df = img_df_feature_prep(label_df)
    prev_count = label_df.shape[0]
    if verbose:
        print(f"Count of items before filtering: {prev_count}")
    label_df = filter_img_df_complement(label_df, options)
    if verbose:
        print(f"Count of filtered items: {label_df.shape[0]}")
    return label_df


if __name__ == '__main__':
    df = image_label_filter(('all',), verbose=True)
    print(df.head())
