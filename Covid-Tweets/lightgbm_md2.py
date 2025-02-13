import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from lightgbm import LGBMClassifier

train = pd.read_csv('train_new.csv')
test = pd.read_csv('test_new.csv')

train = pd.read_csv('train_new.csv')
train = train.fillna(0)

test = pd.read_csv('test_new.csv')
test = test.fillna(0)

test_id = test['Id']
test = test.drop(columns = ['Id', 'text', 'reply_to_screen_name', 'hashtags', 'clean_tweet'], axis = 1)

## Defining input and target
X = train.drop(columns = ['text', 'reply_to_screen_name', 'hashtags', 'clean_tweet', 'country'], axis = 1)
Y = train['country']
Y = np.where(Y == 'us', 0, 
             np.where(Y == 'uk', 1, 
                      np.where(Y == 'canada', 2, 
                               np.where(Y == 'australia', 3,
                                        np.where(Y == 'ireland', 4, 5)))))

## Defining the hyper-parameter grid
LightGBM_param_grid = {'n_estimators': [300],
                       'max_depth': [5, 7],
                       'num_leaves': [20, 30],
                       'min_data_in_leaf': [15, 20],
                       'learning_rate': [0.01, 0.001],
                       'feature_fraction': [0.8, 1],
                       'lambda_l1': [0, 10],
                       'lambda_l2': [0, 10]
                      }

## Performing grid search with 5 folds
LightGBM_grid_search = GridSearchCV(LGBMClassifier(), LightGBM_param_grid, cv = 5, scoring = 'accuracy', n_jobs = -1, verbose = 3).fit(X, Y)

## Extracting best hyper-parameters
best_params = LightGBM_grid_search.best_params_
print('The best hyper-parameters are:', best_params)

## Extracting the best score
best_score = LightGBM_grid_search.best_score_
print('The best accuracy is:', best_score)

## Extracting the best model
LightGBM_md = LightGBM_grid_search.best_estimator_

## Predicting on the test
LightGBM_pred = LightGBM_md.predict_proba(test)
LightGBM_pred = np.argmax(LightGBM_pred, axis = 1)

## Defining data-frame to be exported
data_out = pd.DataFrame({'Id': test_id, 'Category': LightGBM_pred})
data_out['Category'] = np.where(data_out['Category'] == 0, 'us',
                                np.where(data_out['Category'] == 1, 'uk',
                                         np.where(data_out['Category'] == 2, 'canada',
                                                  np.where(data_out['Category'] == 3, 'australia',
                                                           np.where(data_out['Category'] == 4, 'ireland', 'new_zealand')))))

data_out.to_csv('LightGBM_submission_md2.csv', index = False)


# The best hyper-parameters are: {'feature_fraction': 0.8, 'lambda_l1': 0, 'lambda_l2': 0, 'learning_rate': 0.01, 'max_depth': 7, 'min_data_in_leaf': 15, 'n_estimators': 300, 'num_leaves': 30}

# The best accuracy is: 0.34821666666666673