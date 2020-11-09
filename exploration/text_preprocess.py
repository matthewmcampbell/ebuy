from read_db import get_dfs
import string

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import nltk
import numpy as np
import pandas as pd


nltk.download('stopwords')
nltk.download('wordnet')

df, _, _ = get_dfs()
text_df = df.text


def nlp_preprocess(text_df):
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
    print("NLP BoW Features:\n")
    print(len(vectorizer.get_feature_names()))
    print(vectorizer.get_feature_names())
    text_df = text_df.apply(is_in_check, args=(['super', 'smash', 'bros', 'melee'],))
    return (vectorizer.get_feature_names() + ['super smash bros melee'],
            np.concatenate([X.toarray(), np.array(text_df).reshape(X.shape[0], 1)], axis=1))


def make_df(cols, data):
    df = pd.DataFrame(data=data, columns=cols)
    return df

