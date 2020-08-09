from read_db import get_dfs
import matplotlib.pyplot as plt
import streamlit as st

df, df_imgs, df_bids = get_dfs()
df = df[df.price < 100]
df[(df.price < 20)]
df['price'].hist(bins=20)
st.pyplot()

