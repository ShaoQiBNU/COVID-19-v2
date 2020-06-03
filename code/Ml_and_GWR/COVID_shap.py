# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
利用随机森林等机器学方法建模预测
"""

# load package
import pandas as pd
from sklearn.utils import shuffle
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn import svm
from sklearn import linear_model
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error #均方误差
from sklearn.metrics import mean_absolute_error #平方绝对误差
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import KFold
import scipy
import math
import geopandas as gp
from sklearn import preprocessing
import shap


def feature_importance(shap_values, train_x):
    plt.rcParams['font.sans-serif']=['Times New Roman']#用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False#用来正常显示负号
    
    fig = plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, train_x, plot_type="bar", show=False)
    plt.savefig('./picture/feature_importance_shp.eps', dpi=400)


def feature_importance_summary(shap_values, train_x):
    plt.rcParams['font.sans-serif']=['Times New Roman']#用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False#用来正常显示负号
    fig = plt.figure(figsize=(15, 8))
    shap.summary_plot(shap_values, train_x, show=False)
    plt.savefig('./picture/feature_summary_shp.eps', dpi=400)


# main
if __name__ == '__main__':

    df = gp.GeoDataFrame.from_file("./shp/china_city_distinct_COVID19.shp")
    #epidemicIds = [420100]
    #df = df[~df['id'].isin(epidemicIds)]
    

    clf = RandomForestRegressor(n_estimators=20, min_samples_split=5, max_depth=5)
 
    # 全时间段建模
    df = df[['id','location',
    'rhMean',
    't2mMean',
    'moveInMean',
    'moveOutMea',
    'travelMean',
    'WuhanMean',
    'people', 'GDPTotal', 'DISTANCE',
    'confirmed','confirmLog']]

    df.columns = ['id','location',
    'Rh',
    'T2m',
    'MoveIn',
    'MoveOut',
    'Travel',
    'WP',
    'People', 'GDP',  'WD',
    'confirmed','confirmLog']
    
    train_y = df['confirmLog']
    train_x = df.drop(['id', 'location', 'confirmLog', 'confirmed'], axis=1)

    model = clf.fit(train_x, train_y)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(train_x)

    feature_importance(shap_values, train_x)

    feature_importance_summary(shap_values, train_x)

    '''
    fig = plt.figure(figsize=(10, 8))
    shap_interaction_values = explainer.shap_interaction_values(train_x)
    shap.summary_plot(shap_interaction_values, train_x)
    plt.savefig('./picture/feature_interaction_shp.eps', dpi=400)
    plt.show()
    '''