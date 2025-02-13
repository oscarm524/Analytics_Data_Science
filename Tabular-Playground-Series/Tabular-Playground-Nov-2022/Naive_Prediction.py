import boto3
import pandas as pd; pd.set_option('display.max_columns', 100)
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold
# from sklearn.linear_model import LogisticRegression

s3 = boto3.resource('s3')
bucket_name = 'analytics-data-science-competitions'
bucket = s3.Bucket(bucket_name)

file_key_1 = 'Tabular-Playground-Series/Tabular-Playground-Nov-2022/sample_submission.csv'

bucket_object_1 = bucket.Object(file_key_1)
file_object_1 = bucket_object_1.get()
file_content_stream_1 = file_object_1.get('Body')

## Reading data-files
submission = pd.read_csv(file_content_stream_1)
df = pd.read_parquet('s3://analytics-data-science-competitions/Tabular-Playground-Series/Tabular-Playground-Nov-2022/preds_concat_gzip.parquet', engine = 'fastparquet')

## train and test
preds_df = df.clip(0, 1) 
train = preds_df[preds_df['target'].notnull()]
test = preds_df[preds_df['target'].isnull()] 

## Reading logloss data 
logloss_data = pd.read_csv('logloss_data.csv')

def select_logloss_data(train, test, logloss_data, numb):
    
    data_temp = logloss_data.iloc[0:numb, ]
    data_temp['w'] = 1 / data_temp['LogLoss']
    tot = np.sum(data_temp['w'])
    data_temp['W'] = data_temp['w'] / tot
    
    X = train[logloss_data['File'][0:numb].values]
    Y = train['target']
    test_new = test[logloss_data['File'][0:numb].values]
    
    return [X, Y, test_new, data_temp['weight']]
    
out = select_logloss_data(train, test, logloss_data, 100)
X = out[0]
Y = out[1]
test_new = out[2]
w = out[3]

## Defining list to store results
naive_results, test_preds_naive = list(), list()

fold = 1
kfold = StratifiedKFold(n_splits = 5, shuffle = True)
        
for train_ix, test_ix in kfold.split(X, Y):
    
    ## Splitting the data 
    X_train, X_test = X.iloc[train_ix], X.iloc[test_ix]
    Y_train, Y_test = Y.iloc[train_ix], Y.iloc[test_ix]

    ## Predicting on test
    naive_pred
    logit_pred = logit_md.predict_proba(X_test)[:, 1]
    score = log_loss(Y_test, logit_pred)
    logit_results.append(score)
        
    print('Fold ', str(fold), ' result is:', score, '\n')

    test_preds_logit.append(logit_md.predict_proba(test_new)[:, 1])
    fold +=1

print('The average log-loss over 5-fold CV is', np.mean(logit_results))

test_preds_logit = pd.DataFrame(test_preds_logit)
print(test_preds_logit.shape)

test_preds_logit = test_preds_logit.mean(axis = 0)
print(test_preds_logit.head())

submission['pred'] = test_preds_logit
print(submission.head())

submission.to_csv('submission_logistic_liblinear_l1_500.csv', index = False)