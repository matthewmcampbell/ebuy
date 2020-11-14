from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.inspection import permutation_importance
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

# Split into X, y.
features = [col for col in df_clean.columns if col != 'price']
X = df_clean[features]
y = df_clean['price']

# Baseline MSE using y_bar to predict y.
MSE = ((y - y.mean())**2).mean()
print(f'Baseline MSE: {MSE}')

# Fit modeling with below parameters
tree_params = {
    "max_depth": 20,  # Controls depth of tree
    "random_state": 0,  # Allows for determinism
    "ccp_alpha": 1.0  # Allows for min cost complexity pruning if >0.
}
boosting_params = {
    "loss": "ls",  # loss function
    "random_state": 0,

}
# regressor = DecisionTreeRegressor(**tree_params)
regressor = GradientBoostingRegressor(**boosting_params)
cv = cross_val_score(regressor, X, y, cv=5)
print(cv)
fit_model = regressor.fit(X, y)

importance = fit_model.feature_importances_
for i, item in enumerate(features):
    if importance[i] > 0.01:
        print(item, importance[i])


# Permutation importance
perm_importance = permutation_importance(fit_model, X, y)
for i, item in enumerate(features):
    if perm_importance.importances_mean[i] > 0.01:
        print(item, perm_importance.importances_mean[i])
