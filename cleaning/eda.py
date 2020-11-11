from cleaning.read_db import get_dfs
from cleaning.label_df_cleaning import join_to_main_df as img_join
from cleaning.text_preprocess import nlp_join, make_nlp_df
import streamlit as st

# Supply user with choices for df filtering
filter_opts = (
    'Exclude Multiple Cases',
    'Exclude Multiple Discs',
    'Exclude Irrelevant* Items',
    'Apply All Filters'
)
img_filters = st.sidebar.multiselect(
    'Filter Based on Image Criteria',
    filter_opts,
    ('Apply All Filters', )
)

# Map displayed filter to appropriate input param for get_filtered_img_df
img_filter_mapping = dict(zip(filter_opts, ('cases', 'discs', 'irr', 'all')))
filter_choices = [img_filter_mapping[choice] for choice in img_filters]
# img_label_df = image_label_filter_complement(filter_choices)

# Allow price thresholding
min_price = st.sidebar.slider('Min Price', 0, 50, 0)
max_price = st.sidebar.slider('Max Price', 50, 200, 200)

# Read in data from PSQL
df, df_imgs, df_bids = get_dfs()


# Perform NLP formatting
@st.cache
def get_nlp_df(df):
    nlp_df = make_nlp_df(df)
    rename_cols = []
    for col in nlp_df.columns:
        if col in df.columns and col != 'id':
            rename_cols.append(col)
    rename_map = {col: col + '(w)' for col in rename_cols}
    return nlp_df.rename(columns=rename_map)


# Collect NLP data with above method.
nlp_df = get_nlp_df(df)


@st.cache
def df_filtering(df, prices, img_opts='all', nlp=True, **kwargs):
    min_price, max_price = prices
    if img_opts:
        df = img_join(df, img_opts, **kwargs)
    if nlp:
        df = nlp_join(df, nlp_df)
    df = df[(df.price > min_price) & (df.price <= max_price)]
    return df


# Filter out based on image filtering criteria
df = df_filtering(df, (min_price, max_price), img_filters)

# Filtering down by price
st.markdown("## Master dataframe")
df
st.markdown('## Price Distribution')
df['price'].hist(bins=30)
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
df_bid_duration = df[df.bid_duration.str.contains('day')].copy()
df_bid_duration['Numeric_duration'] = df_bid_duration.apply(
    lambda row: row.bid_duration.split()[0], axis=1
).astype(int)
df_bid_duration.plot(kind='scatter', x='Numeric_duration', y='price')
st.pyplot()

st.markdown('## Price vs Rating Count')
df.plot(kind='scatter', x='rating_count', y='price')
st.pyplot()

st.markdown('## Price vs Seller Score')
df.plot(kind='scatter', x='seller_score', y='price')
st.pyplot()

st.markdown('## Price vs Seller Percent')
df.plot(kind='scatter', x='seller_percent', y='price')
st.pyplot()
