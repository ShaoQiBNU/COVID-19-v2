# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
整合所有的特征和疫情数据
"""

# load package
import pandas as pd
from sklearn.utils import shuffle
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error #均方误差
from sklearn.metrics import mean_absolute_error #平方绝对误差
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import KFold
import scipy
import math
import geopandas as gp

# 整合所有特征和label
def get_feature_final():

    # GDP people
    gdp_people = pd.read_csv("./data/gdp_people/china_gdp_people.csv")
    gdp_people = gdp_people[['id', 'people', 'GDPTotal', 'GDPPerson']]

    # 1000 hPa relative humidity
    rh = pd.read_csv("./data/ECMWF/zonal_statistics/city_rh_final.csv")

    # 2m temperature
    t2m = pd.read_csv("./data/ECMWF/zonal_statistics/city_t2m_final.csv")

    # npp
    npp = pd.read_csv("./data/npp/city_npp.csv")

    # rh t2m npp
    df_all = pd.merge(rh, t2m, how='inner', on='id')
    df_all = pd.merge(df_all, npp, how='left', on='id')
    df_all = pd.merge(df_all, gdp_people, how='left', on='id')

    # covid
    covid = pd.read_csv("./output/COVID_city_distinct.csv")

    # merge covid 缺失表示无疫情相关，用0替代
    df_all = pd.merge(df_all, covid, how='left', on='id')
    df_all = df_all.fillna(0)

    # 增加迁入迁徙规模指数、迁出迁徙规模指数和城内出行强度
    moveIn = pd.read_csv("./data/baidu_migration/city_migration.csv")
    df_all = pd.merge(df_all, moveIn, how='left', on='id')
    df_all = df_all.fillna(0)

    # add moveIn from Wuhan
    moveIn_sum = pd.read_csv("./data/baidu_migration/city_move_in_from_WuHan_sum.csv")
    moveIn_sum = moveIn_sum.drop(['name', 'city_baidu_id'], axis=1)
    df_all = pd.merge(df_all, moveIn_sum, how='left', on='id')
    df_all = df_all.fillna(0)
    df_all = df_all.drop_duplicates()

    # 去除台湾,香港,澳门,三沙,铁门关市,双河市,可克达拉市
    df_all = df_all[~df_all['id'].isin(['710000', '810000', '820000', '659006', '659007', '659008', '460300'])]

    # 对label做log变换
    temp = df_all['confirmed'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'confirmed_log'] = temp

    temp = df_all['cured'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'cured_log'] = temp
    
    temp = df_all['dead'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'dead_log'] = temp

    temp = df_all['confirmed_before'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'confirmed_before_log'] = temp

    temp = df_all['cured_before'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'cured_before_log'] = temp
    
    temp = df_all['dead_before'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'dead_before_log'] = temp

    temp = df_all['confirmed_after'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'confirmed_after_log'] = temp

    temp = df_all['cured_after'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'cured_after_log'] = temp
    
    temp = df_all['dead_after'].to_list()
    temp = [math.log(i+1) for i in temp]
    df_all.loc[:, 'dead_after_log'] = temp

    import collections
    print([item for item, count in collections.Counter(df_all['id']).items() if count > 1])

    df_all.to_csv("./output/COVID_final.csv", index=False)


# 将数据与shp文件整合
def get_shp_final():
    df_all = pd.read_csv("./output/COVID_final.csv")

    df = df_all[['id', 'npp', 'location',
                 'rh_mean', 'rh_max', 'rh_min',
                 't2m_mean', 't2m_max', 't2m_min',
                 'confirmed', 'cured', 'dead',
                 'moveIn_index_mean', 'moveIn_index_max', 'moveIn_index_min',
                 'moveOut_index_mean', 'moveOut_index_max', 'moveOut_index_min',
                 'travel_index_mean', 'travel_index_max', 'travel_index_min',
                 '420100_moveIn_mean', '420100_moveIn_max', '420100_moveIn_min',
                 'confirmed_log', 'cured_log', 'dead_log',
                 'people', 'GDPTotal', 'GDPPerson']]

    df.columns = ['id', 'npp', 'location',
                  'rhMean', 'rhMax', 'rhMin',
                  't2mMean', 't2mMax', 't2mMin',
                  'confirmed', 'cured', 'dead',
                  'moveInMean', 'moveInMax', 'moveInMin',
                  'moveOutMean', 'moveOutMax', 'moveOutMin',
                  'travelMean', 'travelMax', 'travelMin',
                  'WuhanMean', 'WuhanMax', 'WuhanMin',
                  'confirmLog', 'curedLog', 'deadLog',
                  'people', 'GDPTotal', 'GDPPerson']

    df_before = df_all[['id', 'npp', 'location',
                        'rh_mean_before', 'rh_max_before', 'rh_min_before',
                        't2m_mean_before', 't2m_max_before', 't2m_min_before',
                        'confirmed_before', 'cured_before', 'dead_before',
                        'moveIn_index_mean_before', 'moveIn_index_max_before', 'moveIn_index_min_before',
                        'moveOut_index_mean_before', 'moveOut_index_max_before', 'moveOut_index_min_before',
                        'travel_index_mean_before', 'travel_index_max_before', 'travel_index_min_before',
                        '420100_moveIn_mean_before', '420100_moveIn_max_before', '420100_moveIn_min_before',
                        'confirmed_before_log', 'cured_before_log', 'dead_before_log',
                        'people', 'GDPTotal', 'GDPPerson']]

    df_before.columns = ['id', 'npp', 'location',
                         'rhMean', 'rhMax', 'rhMin',
                         't2mMean', 't2mMax', 't2mMin',
                         'confirmed', 'cured', 'dead',
                         'moveInMean', 'moveInMax', 'moveInMin',
                         'moveOutMean', 'moveOutMax', 'moveOutMin',
                         'travelMean', 'travelMax', 'travelMin',
                         'WuhanMean', 'WuhanMax', 'WuhanMin',
                         'confirmLog', 'curedLog', 'deadLog',
                         'people', 'GDPTotal', 'GDPPerson']

    df_after = df_all[['id', 'npp', 'location',
                       'rh_mean_after', 'rh_max_after', 'rh_min_after',
                       't2m_mean_after', 't2m_max_after', 't2m_min_after',
                       'confirmed_after', 'cured_after', 'dead_after',
                       'moveIn_index_mean_after', 'moveIn_index_max_after', 'moveIn_index_min_after',
                       'moveOut_index_mean_after', 'moveOut_index_max_after', 'moveOut_index_min_after',
                       'travel_index_mean_after', 'travel_index_max_after', 'travel_index_min_after',
                       '420100_moveIn_mean_after', '420100_moveIn_max_after', '420100_moveIn_min_after',
                       'confirmed_after_log', 'cured_after_log', 'dead_after_log',
                       'people', 'GDPTotal', 'GDPPerson']]

    df_after.columns = ['id', 'npp', 'location',
                        'rhMean', 'rhMax', 'rhMin',
                        't2mMean', 't2mMax', 't2mMin',
                        'confirmed', 'cured', 'dead',
                        'moveInMean', 'moveInMax', 'moveInMin',
                        'moveOutMean', 'moveOutMax', 'moveOutMin',
                        'travelMean', 'travelMax', 'travelMin',
                        'WuhanMean', 'WuhanMax', 'WuhanMin',
                        'confirmLog', 'curedLog', 'deadLog',
                        'people', 'GDPTotal', 'GDPPerson']

    # 2015 China city shp
    path = './shp/china_city_UTM_final.shp'
    shp_city = gp.GeoDataFrame.from_file(path)
    shp_city.rename(columns={'city_id': 'id'}, inplace=True)

    shp_city_all = pd.merge(shp_city, df, how='inner', on='id')
    shp_city_all.to_file("./shp/china_city_distinct_COVID19.shp", encoding='utf-8')
    print(len(shp_city_all))

    shp_city_before = pd.merge(shp_city, df_before, how='inner', on='id')
    shp_city_before.to_file("./shp/china_city_distinct_COVID19_before.shp", encoding='utf-8')
    print(len(shp_city_before))

    shp_city_after = pd.merge(shp_city, df_after, how='inner', on='id')
    shp_city_after.to_file("./shp/china_city_distinct_COVID19_after.shp", encoding='utf-8')
    print(len(shp_city_after))


# main
if __name__ == '__main__':

    # 整合特征
    get_feature_final()
    get_shp_final()