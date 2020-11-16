import string
import nltk
import numpy as np
import pandas as pd

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer

nltk.download('stopwords')
nltk.download('wordnet')


def nlp_preprocess(text_df, verbose=False):
    """Method performing a common Bag-of-Words data_readiness routine.
    All steps taken here include removing punctuation, removing
    stop words, lemmatizing, and a check to see if 'super smash
    bros melee' is in the string. The last of these could likely
    be a relevant feature. Resulting word list is then filtered
    based on tf-idf in a CountVectorizer.
    Args:
        text_df: pd.DataFrame
        verbose: bool
    Returns:
        (list, np.array) where the list contains feature names from bag-of-words
        and the numpy array is an indicator matrix for features."""
    def remove_punctuation(text):
        no_punct = "".join([c for c in text if c not in string.punctuation])
        return no_punct

    def remove_stops(text):
        no_stops = [w for w in text if (w not in stopwords.words('english') or w in ['not', 'no'])]
        return no_stops

    lemmatizer = WordNetLemmatizer()

    def word_lemmatizer(text):
        lem_text = [lemmatizer.lemmatize(i) for i in text]
        return lem_text

    def is_in_check(text, words):
        for word in words:
            if word not in text:
                return 0
        return 1

    tokenizer = RegexpTokenizer(r'\w+')

    text_df = text_df.apply(remove_punctuation)
    text_df = text_df.apply(lambda x: tokenizer.tokenize(x.lower()))
    text_df = text_df.apply(word_lemmatizer)
    text_df = text_df.apply(remove_stops)
    text = [" ".join(x) for x in text_df]
    vectorizer = CountVectorizer(min_df=0.02, max_df=0.65, ngram_range=(1, 2))
    X = vectorizer.fit_transform(text)
    if verbose:
        print("NLP BoW Features:\n")
        print(len(vectorizer.get_feature_names()))
        print(vectorizer.get_feature_names())
    text_df = text_df.apply(is_in_check, args=(['super', 'smash', 'bros', 'melee'],))
    return (vectorizer.get_feature_names() + ['super smash bros melee'],
            np.concatenate([X.toarray(), np.array(text_df).reshape(X.shape[0], 1)], axis=1))


def get_nlp_df(df, **kwargs):
    """Calls the nlp_preprocess method and pushes
    output into a dataframe for easy joining.
    Args:
        df: pd.DataFrame (the main dataframe)
    Returns:
        df: pd.DataFrame (dataframe made through
        nlp process)"""
    ids = df.id
    cols, data = nlp_preprocess(df.text, **kwargs)
    nlp_df = pd.DataFrame(data=data, columns=cols)
    nlp_df['id'] = ids

    rename_cols = []
    for col in nlp_df.columns:
        if col in df.columns and col != 'id':
            rename_cols.append(col)
    rename_map = {col: col + '(w)' for col in rename_cols}
    return nlp_df.rename(columns=rename_map)


def nlp_join(df, nlp_df):
    """Joins the nlp dataframe to the main dataframe.
    Args:
        df: pd.DataFrame (main df)
        nlp_df: pd.DataFrame
    Returns:
        pd.DataFrame"""
    return df.merge(nlp_df, on='id', how='left')
