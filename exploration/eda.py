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
accept_conditions_df = df.cond.value_counts()
accept_conditions = accept_conditions_df[accept_conditions_df > 10]
accept_conditions = list(
    dict(accept_conditions).keys()
)
df[df.cond.isin(accept_conditions)].plot(kind='scatter', x='cond', y='price')
st.pyplot()

st.markdown('## Price vs Bid Duration')
df_bid_duration = df[df.bid_duration.str.contains('day')]
df_bid_duration['Numeric_duration'] = df_bid_duration.apply(lambda row: row.bid_duration.split()[0], axis=1).astype(int)
# df[df.bid_duration.str.contains('day')].plot(kind='scatter', x='bid_duration', y='price')
df_bid_duration.plot(kind='scatter', x='Numeric_duration', y='price')
st.pyplot()

st.markdown('## Price vs Rating Count')
df.plot(kind='scatter', x='rating_count', y='price')
st.pyplot()

st.markdown('## Price vs Seller Score')
df.plot(kind='scatter', x='seller_score', y='price')
st.pyplot()
