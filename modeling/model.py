from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
import modeling.prep as prep
from data_collection.misc import read_yaml
import os
import pandas as pd

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
csv_path = config['csv_path']
data_path = csv_path + 'train.csv'

# Read in data and handle missing values.
df = prep.read_data(data_path)
df_clean = prep.handle_missing(df)

# for col in df_clean.columns:
#     print(col, type(df_clean[col].dtypes))
# exit(0)

# Split into X, y.
X = df_clean[[col for col in df_clean.columns if col != 'price']]
y = df_clean['price']

# Fit modeling with below parameters
model_params = {
    "max_depth": 20,  # Controls depth of tree
    "random_state": 0,  # Allows for determinism
    "ccp_alpha": 1.0  # Allows for min cost complexity pruning if >0.
}

regressor = DecisionTreeRegressor(**model_params)
cv = cross_val_score(regressor, X, y, cv=10)
print(cv)
