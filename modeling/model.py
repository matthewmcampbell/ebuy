import os

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import ElasticNet

import modeling.prep as prep
from data_collection.misc import read_yaml

folder = os.path.dirname(__file__)
config_file = os.path.join(folder, '..', 'conf.yaml')
config = read_yaml(config_file)
csv_path = config['csv_path']
data_path = csv_path + 'train.csv'

# Control whether we search for hyper-parameters
hyper_param_search = True

# Read in data and handle missing values.
df = prep.read_data(data_path)
df_clean = prep.handle_missing(df)

# Split into X, y.
features = [col for col in df_clean.columns if col != 'price']
X = df_clean[features]
y = df_clean['price']

# Standardize features
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)

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
    "n_estimators": 50,
    "subsample": 0.8
}
svm_params = {
    "kernel": 'poly'
}

elastic_params = {
    "alpha": 1,
    "random_state": 0,

}
# regressor = DecisionTreeRegressor(**tree_params)
# regressor = GradientBoostingRegressor(**boosting_params)
# regressor = SVR(**svm_params)
# regressor = ElasticNet(**elastic_params)

if hyper_param_search:
    alphas = [2**i for i in range(-3, 2)]
    l1_ratios = [i/10 for i in range(1, 11)]
    best_mse = -1*MSE
    best_alpha, best_l1 = alphas[0], l1_ratios[0]
    for alpha in alphas:
        for l1_ratio in l1_ratios:
            regressor = ElasticNet(alpha=alpha, l1_ratio=l1_ratio,
                                   random_state=0, max_iter=5000, tol=.1)
            cv = cross_val_score(regressor, X, y,
                                 cv=5, scoring='neg_mean_squared_error')
            print(f"Params alpha {alpha}, l1_ratio {l1_ratio}, cvMSE {cv.mean()}")
            if cv.mean() > best_mse:
                best_mse = cv.mean()
                best_alpha, best_l1 = alpha, l1_ratio
else:
    best_alpha, best_l1 = 0.25, 1  # Determined from prior experimentation.

print(best_alpha, best_l1)
regressor = ElasticNet(alpha=best_alpha, l1_ratio=best_l1, random_state=0)
fit_model = regressor.fit(X, y)

# Analysis on most relevant predictors.
df_coef = pd.DataFrame({'feature': features, 'coef': fit_model.coef_})
print('Most negative contributors to sell price:')
print(df_coef.sort_values(by='coef').head(10))
print('Most positive contributors to sell price:')
print(df_coef.sort_values(by='coef').tail(10))


# importance = fit_model.feature_importances_
# print('Feature Importance based on impurity:')
# for i, item in enumerate(features):
#     if importance[i] > 0.01:
#         print(item, importance[i])
#
#
# # Permutation importance
# perm_importance = permutation_importance(fit_model, X, y)
# print('\n\nFeature Importance based on permutations.')
# for i, item in enumerate(features):
#     if perm_importance.importances_mean[i] > 0.01:
#         print(item, perm_importance.importances_mean[i])
