from read_db import get_dfs
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

df, df_imgs, df_bids = get_dfs()
df = df[df.price < 100]
st.markdown("## Master dataframe")
df
df['cond'].value_counts().plot(kind='bar')
st.pyplot()
df.plot(kind='scatter', x='cond', y='price')
st.pyplot()
df['price'].hist(bins=20)
st.pyplot()
df.plot(kind='scatter', x='bid_duration', y='price')
st.pyplot()
df['rating_count'] = df['rating_count'].astype(str)
df.plot(kind='scatter', x='rating_count', y='price')
st.pyplot()

