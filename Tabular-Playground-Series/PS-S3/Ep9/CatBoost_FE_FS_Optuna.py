import boto3
import pandas as pd; pd.set_option('display.max_columns', 100)
import numpy as np

from tqdm import tqdm

import matplotlib.pyplot as plt; plt.style.use('ggplot')
import seaborn as sns

from scipy.stats import rankdata
from sklearn.multiclass import OneVsRestClassifier
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold, train_test_split, GridSearchCV, StratifiedKFold, TimeSeriesSplit
from sklearn.feature_selection import RFE, RFECV
from sklearn.metrics import mean_squared_error, roc_auc_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier, LGBMRegressor 
from xgboost import XGBClassifier, XGBRegressor
from catboost import CatBoostClassifier, CatBoostRegressor

import optuna 

s3 = boto3.resource('s3')
bucket_name = 'analytics-data-science-competitions'
bucket = s3.Bucket(bucket_name)

file_key_1 = 'Tabular-Playground-Series/PS-S3/Ep9/train.csv'
file_key_2 = 'Tabular-Playground-Series/PS-S3/Ep9/test.csv'
file_key_3 = 'Tabular-Playground-Series/PS-S3/Ep9/sample_submission.csv'

bucket_object_1 = bucket.Object(file_key_1)
file_object_1 = bucket_object_1.get()
file_content_stream_1 = file_object_1.get('Body')

bucket_object_2 = bucket.Object(file_key_2)
file_object_2 = bucket_object_2.get()
file_content_stream_2 = file_object_2.get('Body')

bucket_object_3 = bucket.Object(file_key_3)
file_object_3 = bucket_object_3.get()
file_content_stream_3 = file_object_3.get('Body')

## Reading data files
train = pd.read_csv(file_content_stream_1)

train_no_dup = train.drop(columns = 'id', axis = 1)
train_no_dup = pd.DataFrame(train_no_dup.groupby(train_no_dup.columns.tolist()[0:8])['Strength'].mean()).reset_index()

X = train_no_dup.drop(columns = ['Strength'], axis = 1)
Y = train_no_dup['Strength']


#########################
## Feature Engineering ##
#########################

def feature_engineering(df):

    df['amount'] = df[['CementComponent', 'BlastFurnaceSlag', 'FlyAshComponent', 'WaterComponent', 'SuperplasticizerComponent', 'CoarseAggregateComponent', 'FineAggregateComponent']].sum(axis=1)
    df['CementComponent_ratio'] = df['CementComponent'] / (df['amount'] + 1e-6)
    df['BlastFurnaceSlag_ratio'] = df['BlastFurnaceSlag'] / (df['amount'] + 1e-6)
    df['FlyAshComponent_ratio'] = df['FlyAshComponent'] / (df['amount'] + 1e-6)
    df['WaterComponent_ratio'] = df['WaterComponent'] / (df['amount'] + 1e-6)
    df['SuperplasticizerComponent_ratio'] = df['SuperplasticizerComponent'] / (df['amount'] + 1e-6)
    df['SuperplasticizerComponent_ratio'] = df['SuperplasticizerComponent'] / (df['amount'] + 1e-6)
    df['FineAggregateComponent_ratio'] = df['FineAggregateComponent'] / (df['amount'] + 1e-6)
    
    # ratio to cement
    df['BlastFurnaceSlag_to_Cement_ratio'] = df['BlastFurnaceSlag'] / (df['CementComponent'] + 1e-6)
    df['FlyAshComponent_to_Cement_ratio'] = df['FlyAshComponent'] / (df['CementComponent'] + 1e-6)
    df['WaterComponent_to_Cement_ratio'] = df['WaterComponent'] / (df['CementComponent'] + 1e-6)
    df['SuperplasticizerComponent_to_Cement_ratio'] = df['SuperplasticizerComponent'] / (df['CementComponent'] + 1e-6)
    df['CoarseAggregateComponent_to_Cement_ratio'] = df['CoarseAggregateComponent'] / (df['CementComponent'] + 1e-6)
    df['FineAggregateComponent_to_Cement_ratio'] = df['FineAggregateComponent'] / (df['CementComponent'] + 1e-6)
    
    # other ratio
    df['SuperplasticizerComponent_to_FlyAshComponent_ratio'] = df['SuperplasticizerComponent'] / (df['FlyAshComponent'] + 1e-6)
    df['SuperplasticizerComponent_to_WaterComponent_ratio'] = df['SuperplasticizerComponent'] / (df['WaterComponent'] + 1e-6)
    df['CoarseAggregateComponent_to_FineAggregateComponent_ratio'] = df['CoarseAggregateComponent'] / (df['FineAggregateComponent'] + 1e-6)
    
    return df

train_no_dup = feature_engineering(train_no_dup)

X = train_no_dup.drop(columns = ['Strength'], axis = 1)
Y = train_no_dup['Strength']


#######################
## Feature Selection ##
#######################

print('-----------------------------------')
print(' (-: Feature Selection Started :-) ')
print('-----------------------------------')

## Running RFECV multiple times
RFE_results = list()

for i in tqdm(range(0, 10)):
    
    auto_feature_selection = RFECV(estimator = CatBoostRegressor(iterations = 100, verbose = False), step = 1, min_features_to_select = 2, cv = 5, scoring = 'neg_root_mean_squared_error', n_jobs = -1).fit(X, Y)
    
    ## Extracting and storing features to be selected
    RFE_results.append(auto_feature_selection.support_)

## Changing to data-frame
RFE_results = pd.DataFrame(RFE_results)
RFE_results.columns = X.columns

## Computing the percentage of time features are flagged as important
RFE_results = 100*RFE_results.apply(np.sum, axis = 0) / RFE_results.shape[0]

## Identifying features with a percentage score > 80%
features_to_select = RFE_results.index[RFE_results > 80].tolist()
print(features_to_select)


############
## Optuna ##
############

print('------------------------------------')
print(' (-: Optuna Optimization Started :-)')
print('------------------------------------')

X = train_no_dup[features_to_select]
Y = train_no_dup['Strength']

class Objective:

    def __init__(self, seed):
        # Hold this implementation specific arguments as the fields of the class.
        self.seed = seed

    def __call__(self, trial):
        ## Parameters to be evaluated
        param = dict(loss_function = 'RMSE',
                     iterations = trial.suggest_int('iterations', 300, 10000),
                     learning_rate = trial.suggest_float('learning_rate', 0.001, 1, log = True),
                     depth = trial.suggest_int('depth', 3, 12),
                     random_strength = trial.suggest_float('random_strength', 0.01, 10.0, log = True),
                     bagging_temperature = trial.suggest_float('bagging_temperature', 0.01,  0.99),
                     border_count = trial.suggest_int('border_count', 1, 255),
                     l2_leaf_reg = trial.suggest_int('l2_leaf_reg', 2, 30),
                     verbose = False
                    )

        scores = []
        
        skf = KFold(n_splits = 5, shuffle = True, random_state = self.seed)

        for train_idx, valid_idx in skf.split(X, Y):

            X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
            Y_train , Y_valid = Y.iloc[train_idx] , Y.iloc[valid_idx]

            model = CatBoostRegressor(**param).fit(X_train, Y_train)
            preds_valid = model.predict(X_valid)

            score = mean_squared_error(Y_valid, preds_valid, squared = False)
            scores.append(score)

        return np.mean(scores)
    
## Defining number of runs and seed
SEED = 42
N_TRIALS = 70

# Execute an optimization
study = optuna.create_study(direction = 'minimize')
study.optimize(Objective(SEED), n_trials = N_TRIALS)

optuna_hyper_params = pd.DataFrame.from_dict([study.best_trial.params])
file_name = 'CatBoost_Seed_FE_FS_' + str(SEED) + '_Optuna_Hyperparameters.csv'
optuna_hyper_params.to_csv(file_name, index = False)
