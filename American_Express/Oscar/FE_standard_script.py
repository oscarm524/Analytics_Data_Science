import boto3
import pandas as pd
import numpy as np

s3 = boto3.resource('s3')
bucket_name = 'analytics-data-science-competitions'
bucket = s3.Bucket(bucket_name)

## Defining files names
file_key_1 = 'AmericanExpress/train_data.csv'
# file_key_2 = 'AmericanExpress/train_labels.csv'

bucket_object_1 = bucket.Object(file_key_1)
file_object_1 = bucket_object_1.get()
file_content_stream_1 = file_object_1.get('Body')

# bucket_object_2 = bucket.Object(file_key_2)
# file_object_2 = bucket_object_2.get()
# file_content_stream_2 = file_object_2.get('Body')

## Creating data-type dictionary for reading the train data-frame
# dtype_dict = {'customer_ID': "object", 'S_2': "object", 'P_2': 'float16', 'D_39': 'float16', 'B_1': 'float16','B_2': 'float16',
#               'R_28': 'float16','S_3': 'float16','D_41': 'float16','B_3': 'float16','D_42': 'float16','D_43': 'float16','D_44': 'float16',
#               'B_4': 'float16','D_45': 'float16','B_5': 'float16','R_28': 'float16','D_46': 'float16','D_47': 'float16','D_48': 'float16',
#               'D_49': 'float16','B_6': 'float16','B_7': 'float16','B_8': 'float16','D_50': 'float16','D_51': 'float16','B_9': 'float16',
#               'R_28': 'float16','D_52': 'float16','P_3': 'float16','B_10': 'float16','D_53': 'float16','S_5': 'float16','B_11': 'float16',
#               'S_6': 'float16','D_54': 'float16','R_28': 'float16','S_7': 'float16','B_12': 'float16','S_8': 'float16','D_55': 'float16',
#               'D_56': 'float16','B_13': 'float16','R_28': 'float16','D_58': 'float16','S_9': 'float16','B_14': 'float16','D_59': 'float16',
#               'D_60': 'float16','D_61': 'float16','B_15': 'float16','S_11': 'float16','D_62': 'float16','D_63': 'object','D_64': 'object',
#               'D_65': 'float16','B_16': 'float16','B_17': 'float16','B_18': 'float16','B_19': 'float16','D_66': 'float16','B_20': 'float16',
#               'D_68': 'float16','S_12': 'float16','R_28': 'float16','S_13': 'float16','B_21': 'float16','D_69': 'float16','B_22': 'float16',
#               'D_70': 'float16','D_71': 'float16','D_72': 'float16','S_15': 'float16','B_23': 'float16','D_73': 'float16','P_4': 'float16',
#               'D_74': 'float16','D_75': 'float16','D_76': 'float16','B_24': 'float16','R_28': 'float16','D_77': 'float16','B_25': 'float16',
#               'B_26': 'float16','D_78': 'float16','D_79': 'float16','R_28': 'float16','R_9': 'float16','S_16': 'float16','D_80': 'float16',
#               'R_280': 'float16','R_281': 'float16','B_27': 'float16','D_81': 'float16','D_82': 'float16','S_17': 'float16','R_282': 'float16',
#               'B_28': 'float16','R_283': 'float16','D_83': 'float16','R_284': 'float16','R_285': 'float16','D_84': 'float16','R_286': 'float16',
#               'B_29': 'float16','B_30': 'float16','S_18': 'float16','D_86': 'float16','D_87': 'float16','R_287': 'float16','R_288': 'float16',
#               'D_88': 'float16','B_31': 'int64','S_19': 'float16','R_289': 'float16','B_32': 'float16','S_20': 'float16','R_280': 'float16',
#               'R_281': 'float16','B_33': 'float16','D_89': 'float16','R_282': 'float16','R_283': 'float16','D_91': 'float16','D_92': 'float16',
#               'D_93': 'float16','D_94': 'float16','R_284': 'float16','R_285': 'float16','D_96': 'float16','S_22': 'float16','S_23': 'float16',
#               'S_24': 'float16','S_25': 'float16','S_26': 'float16','D_102': 'float16','D_103': 'float16','D_104': 'float16','D_105': 'float16',
#               'D_106': 'float16','D_107': 'float16','B_36': 'float16','B_37': 'float16', 'R_286': 'float16','R_287': 'float16','B_38': 'float16',
#               'D_108': 'float16','D_109': 'float16','D_110': 'float16','D_111': 'float16','B_39': 'float16','D_112': 'float16','B_40': 'float16',
#               'S_27': 'float16','D_113': 'float16','D_114': 'float16','D_115': 'float16','D_116': 'float16','D_117': 'float16','D_118': 'float16',
#               'D_119': 'float16','D_120': 'float16','D_121': 'float16','D_122': 'float16','D_123': 'float16','D_124': 'float16','D_125': 'float16',
#               'D_126': 'float16','D_127': 'float16','D_128': 'float16','D_129': 'float16','B_41': 'float16','B_42': 'float16','D_130': 'float16',
#               'D_131': 'float16','D_132': 'float16','D_133': 'float16','R_288': 'float16','D_134': 'float16','D_135': 'float16','D_136': 'float16',
#               'D_137': 'float16','D_138': 'float16','D_139': 'float16','D_140': 'float16','D_141': 'float16','D_142': 'float16','D_143': 'float16',
#               'D_144': 'float16','D_145': 'float16'}

dtype_dict = {'customer_ID': 'object', 'R_28': 'float16'}

## Reading data-files
train = pd.read_csv(file_content_stream_1, dtype = dtype_dict, usecols = ['customer_ID', 'R_28'])
# target = pd.read_csv(file_content_stream_2)

risk_features = pd.read_csv('Risk_Features.csv')

## Appending target variables
# train = pd.merge(train, target, on = 'customer_ID', how = 'left')

## Selecting Deliquency variables (and risk variables)
# my_variables = train.columns
# D_variables = [x for x in my_variables if x.startswith('R_')]
# to_select = ['customer_ID', 'target']
# for i in range(2, (len(D_variables) + 2)):
#     to_select.append(D_variables[i-2])

# train_deli = train[to_select]

## Selecting unique customer_ID and target
# customer_target = train[['customer_ID', 'target']].drop_duplicates().reset_index(drop = True)

## Computing basic summary-stats features
def summary_stats(x):
    
    d = {}
    d['R_28_mean'] = x['R_28'].mean()
    d['R_28_median'] = x['R_28'].median()
    d['R_28_min'] = x['R_28'].min()
    d['R_28_max'] = x['R_28'].max()
    d['R_28_range'] = np.where(x['R_28'].shape[0] == 1, 0, x['R_28'].max() - x['R_28'].min())
    d['R_28_IQR'] = np.where(x['R_28'].shape[0] == 1, 0,np.percentile(x['R_28'], 75) - np.percentile(x['R_28'], 25))
    d['R_28_std'] = np.where(x['R_28'].shape[0] == 1, 0, np.std(x['R_28'], ddof = 1))
#     d['R_28_negative_count'] = np.sum(x['R_28'] < 0) 
#     d['R_28_positive_count'] = np.sum(x['R_28'] > 0)
    d['R_28_pct_values_above_mean'] = np.where(x['R_28'].shape[0] == 1, 0, np.sum(x['R_28'] > x['R_28'].mean())/x['R_28'].shape[0])
#     d['R_28_avg_pct_change'] = np.where(x['R_28'].shape[0] == 1, 0, pd.Series(x['R_28'].to_list()).pct_change().mean())
    d['R_28_last_value'] = x['R_28'].iloc[-1]
    
    return pd.Series(d, index = ['R_28_mean', 'R_28_median', 'R_28_min', 'R_28_max', 'R_28_range', 'R_28_IQR', 'R_28_std', 'R_28_pct_values_above_mean', 'R_28_last_value'])

data_out = train.groupby('customer_ID').apply(summary_stats)
data_out['customer_ID'] = data_out.index
data_out = data_out.reset_index(drop = True)

# ## Computing average change at the customer level
# data_change = pd.DataFrame(train_deli.groupby(['customer_ID'])['R_28'].apply(lambda x: pd.Series(x.to_list()).pct_change().mean()))
# data_change['customer_ID'] = data_change.index
# data_change = data_change.reset_index(drop = True)
# data_change.columns = ['R_28_change', 'customer_ID']

# ## Computing change from first to last month
# data_change_first_last = pd.DataFrame(train_deli.groupby(['customer_ID'])['R_28'].apply(lambda x: pd.Series(x.iloc[[0, -1]].to_list()).pct_change())).unstack()
# data_change_first_last = data_change_first_last.drop(columns = ('R_28', 0), axis = 1)
# data_change_first_last['customer_ID'] = data_change_first_last.index
# data_change_first_last = data_change_first_last.reset_index(drop = True)
# data_change_first_last.columns = ['R_28_change_first_last', 'customer_ID']

## Joining the to datasets
# data_out = pd.merge(customer_target, data_out, on = 'customer_ID', how = 'left')
# data_out = data_out.drop(columns = ['target'], axis = 1)

# delinquency_features = pd.merge(delinquency_features, data_out, on = 'customer_ID', how = 'left')
risk_features = pd.merge(risk_features, data_out, on = 'customer_ID', how = 'left')

# data_out = pd.merge(data_avg, data_median, on = 'customer_ID', how = 'left')
# data_out = pd.merge(data_out, data_change, on = 'customer_ID', how = 'left')
# data_out = pd.merge(data_out, data_change_first_last, on = 'customer_ID', how = 'left')

# data_out.to_csv('Risk_Features.csv', index = False)
# delinquency_features.to_csv('Delinquency_Features.csv', index = False)
risk_features.to_csv('Risk_Features.csv', index = False)
