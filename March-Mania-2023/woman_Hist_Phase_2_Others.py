import boto3
import pandas as pd; pd.set_option('display.max_columns', 100)
import numpy as np

import matplotlib.pyplot as plt; plt.style.use('ggplot')
import seaborn as sns

from scipy.stats import rankdata
from sklearn.multiclass import OneVsRestClassifier
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold, train_test_split, GridSearchCV, StratifiedKFold, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, roc_auc_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import HistGradientBoostingRegressor, GradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier, LGBMRegressor 
from xgboost import XGBClassifier, XGBRegressor
from catboost import CatBoostClassifier, CatBoostRegressor

import optuna 

s3 = boto3.resource('s3')
bucket_name = 'analytics-data-science-competitions'
bucket = s3.Bucket(bucket_name)

file_key_1 = 'March-Mania-2023/Evan-Data/MNCAA_train_538.csv'
file_key_2 = 'March-Mania-2023/Evan-Data/MNCAA_test_538.csv'
file_key_3 = 'March-Mania-2023/Evan-Data/WNCAA_train_538.csv'
file_key_4 = 'March-Mania-2023/Evan-Data/WNCAA_test_538.csv'

bucket_object_1 = bucket.Object(file_key_1)
file_object_1 = bucket_object_1.get()
file_content_stream_1 = file_object_1.get('Body')

bucket_object_2 = bucket.Object(file_key_2)
file_object_2 = bucket_object_2.get()
file_content_stream_2 = file_object_2.get('Body')

bucket_object_3 = bucket.Object(file_key_3)
file_object_3 = bucket_object_3.get()
file_content_stream_3 = file_object_3.get('Body')

bucket_object_4 = bucket.Object(file_key_4)
file_object_4 = bucket_object_4.get()
file_content_stream_4 = file_object_4.get('Body')

## Reading data files
man_train = pd.read_csv(file_content_stream_1)
man_test = pd.read_csv(file_content_stream_2)
woman_train = pd.read_csv(file_content_stream_3)
woman_test = pd.read_csv(file_content_stream_4)

man_train['target'] = np.where(man_train['ResultDiff'] > 0, 1, 0)
woman_train['target'] = np.where(woman_train['ResultDiff'] > 0, 1, 0)

to_select = ['Season',
             'X1_WinRatio14d',
             'X1_PointsMean',
             'X1_PointsMedian',
             'X1_PointsDiffMean',
             'X1_FgaMean',
             'X1_FgaMedian',
             'X1_FgaMin',
             'X1_FgaMax',
             'X1_AstMean',
             'X1_BlkMean',
             'X1_OppFgaMean',
             'X1_OppFgaMin',
             'X1_EfgpMean',
             'X1_PossessionsMean',
             'X1_PpmMean',
             'X1_FtrMean',
             'X1_TopMean',
             'X1_DrebpMean',
             'X2_WinRatio14d',
             'X2_PointsMean',
             'X2_PointsMedian',
             'X2_PointsDiffMean',
             'X2_FgaMean',
             'X2_FgaMedian',
             'X2_FgaMin',
             'X2_FgaMax',
             'X2_AstMean',
             'X2_BlkMean',
             'X2_OppFgaMean',
             'X2_OppFgaMin',
             'X2_EfgpMean',
             'X2_PossessionsMean',
             'X2_PpmMean',
             'X2_FtrMean',
             'X2_TopMean',
             'X2_DrebpMean',
             'ResultDiff', 
             'target']

woman_train = woman_train[to_select]


############
## Optuna ##
############

print('------------------------------------')
print(' (-: Optuna Optimization Started :-)')
print('------------------------------------')

class Objective:

    def __init__(self, seed):
        # Hold this implementation specific arguments as the fields of the class.
        self.seed = seed

    def __call__(self, trial):
        
        ## Parameters to be evaluated
        param = dict(l2_regularization = trial.suggest_float('l2_regularization', 0.01, 10.0, log = True),
                     early_stopping = trial.suggest_categorical('early_stopping', [False]),
                     learning_rate = trial.suggest_float('learning_rate', 0.001, 1, log = True),
                     max_iter = trial.suggest_categorical('max_iter', [1000]),
                     max_depth = trial.suggest_int('max_depth', 2, 15),
                     max_bins = trial.suggest_int('max_bins', 100, 255),
                     min_samples_leaf = trial.suggest_int('min_samples_leaf', 20, 100),
                     max_leaf_nodes = trial.suggest_int('max_leaf_nodes', 20, 100)
                    )

        scores = []
        
        for i in range(2013, 2022):
    
            train_data = woman_train[woman_train['Season'] <= i].reset_index(drop = True) 
    
            if ((i + 1) == 2020): 
                continue 
            else:
                test_data = woman_train[woman_train['Season'] == (i + 1)].reset_index(drop = True)
    
            X_train = train_data.drop(columns = ['Season', 'target'], axis = 1)
            Y_train = train_data['target']
            X_valid = test_data.drop(columns = ['Season', 'target'], axis = 1)
            Y_valid = test_data['target']
        
            model = HistGradientBoostingClassifier(**param).fit(X_train, Y_train)
            preds_valid = model.predict_proba(X_valid)[:, 1]

            score = mean_squared_error(Y_valid, preds_valid)
            scores.append(score)

        return np.mean(scores)
    
## Defining SEED and Trials
SEED = 42
N_TRIALS = 50

# Execute an optimization
study = optuna.create_study(direction = 'minimize')
study.optimize(Objective(SEED), n_trials = N_TRIALS)

print('----------------------------------------')
print(' (-: Saving Optuna Hyper-Parameters :-) ')
print('----------------------------------------')

optuna_hyper_params = pd.DataFrame.from_dict([study.best_trial.params])
file_name = 'woman_Hist_Phase_2_Others_' + str(SEED) + '_Optuna_Hyperparameters.csv'
optuna_hyper_params.to_csv(file_name, index = False)
