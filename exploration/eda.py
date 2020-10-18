from read_db import get_dfs
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

min_price = st.sidebar.slider('Min Price', 0, 50, 0)
max_price = st.sidebar.slider('Max Price', 50, 200, 200)

# Read in data from PSQL
df, df_imgs, df_bids = get_dfs()

# Filtering down by price
df = df[(df.price > min_price) & (df.price <= max_price)]

st.markdown("## Master dataframe")
df

st.markdown('## Price Distribution')
df['price'].hist(bins=20)
st.pyplot()

st.markdown('## Condition Counts')
df['cond'].value_counts().plot(kind='bar')
st.pyplot()

st.markdown('## Price vs Condition')
df.plot(kind='scatter', x='cond', y='price')
st.pyplot()

st.markdown('## Price vs Bid Duration')
df.plot(kind='scatter', x='bid_duration', y='price')
st.pyplot()

st.markdown('## Price vs Rating Count')
# df['rating_count'] = df['rating_count'].astype(str)
df.plot(kind='scatter', x='rating_count', y='price')
st.pyplot()

