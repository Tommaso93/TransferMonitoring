import numpy as np
import pandas as pd
from pandas import read_csv
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing
from memory_profiler import memory_usage
import math
from benchmark_conf import atribute_drop_list, model_train_parameter, model_func_l
from utils.timer import Timer
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error

import csv

# functions
log_f = lambda x: math.log(x + 2)
exp_2 = lambda x: math.exp(x) - 2

##--------
# setup

# Here i keep prepared csv file for ML
f = open('/home/zygis/_Projektai/CERN/TransferMonitoring/Zygimantas/data/output/out120000.csv')
# in order to display of dataframe
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_rows', 30)

dataframe = read_csv(f).astype(np.float32)

# save headers to seperate list
original_headers = list(dataframe.columns.values)

# remove lines with error
# dataframe = dataframe[dataframe.timestamp_tr_dlt != -1]

# fields that we drop
for el in atribute_drop_list:
    try:
        dataframe = dataframe.drop(el, axis=1)
    except:
        print('There was no such field:{}'.format(el))

# from dataframe pop target column and transform to ndarray
target = dataframe.pop('timestamp_tr_dlt')

# Scalling data
matrix_to_scale = dataframe.as_matrix()

#  scale between [0;1]
min_max_scaler = preprocessing.MinMaxScaler()
X_scalled = min_max_scaler.fit_transform(matrix_to_scale)

X = X_scalled

y = target.as_matrix()
y = list(map(log_f, y))

min_max_scaler_y = preprocessing.MinMaxScaler()
y = min_max_scaler_y.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=92)
len(X_train), len(X_test)

### -----
# ML phase

# params,model1,..,modeln

# print(X_train)

table = []
for model_n, model_f in model_func_l:
    results_list = []
    for param in model_train_parameter:
        with Timer() as t:
            model = model_f(**param)
            # returns maximu
            mem_usage = memory_usage((model.fit, [X_train, y_train]), max_usage=True)
        y_pred = model.predict(X_test)
        # y_test_f = list(map(exp_2, y_test))
        # y_pred_f = list(map(exp_2, y_pred))
        y_test_f = list(map(exp_2, min_max_scaler_y.inverse_transform(y_test)))
        y_pred_f = list(map(exp_2, min_max_scaler_y.inverse_transform(y_pred)))
        results_d = {
            '1.parameters': param,
            # 'name': str(model_f),
            '2.time_to_train_in_sec': t.secs,
            '3.RAM_usages_in_MiB': max(mem_usage),
            '4.MAE': mean_absolute_error(y_test_f, y_pred_f),
            '5.RMSE': mean_squared_error(y_test_f, y_pred_f)
        }
        results_list.append(results_d)
        # i = 0
        # for answ, pred in zip(y_test_f, y_pred_f):
        #     i +=1
        #     print ('{}=>{}'.format(answ,pred))
        #     if i > 100:
        #         break

    outputhPath = '../../data/output/' + model_n +'.csv'
    keysSet = sorted(results_list[0].keys())

    from jsonUtilities import jsonListToCSV
    jsonListToCSV(results_list,keysSet,outputhPath)

