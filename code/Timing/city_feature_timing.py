# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
生成时间序列数据，并作归一化处理
"""

# load packages
import pandas as pd
import os
import numpy as np
from sklearn.utils import shuffle
from sklearn import preprocessing

# 获取各个城市每天的特征及累计确诊人数
def feature_daily(dates1, dates2, china_city_distinct):

    city_feature_all = []

    # rh
    rh = pd.read_csv("D:\\COVID-19\\data\\ECMWF\\zonal_statistics\\city_rh_day.csv")
    
    # t2m
    t2m = pd.read_csv("D:\\COVID-19\\data\\ECMWF\\zonal_statistics\\city_t2m_day.csv")

    # moveIn
    moveIn = pd.read_csv("D:\\COVID-19\\data\\baidu_migration\\city_moveIn.csv")

    # moveOut
    moveOut = pd.read_csv("D:\\COVID-19\\data\\baidu_migration\\city_moveOut.csv")

    # travel
    travel = pd.read_csv("D:\\COVID-19\\data\\baidu_migration\\city_travel.csv")

    # 武汉迁入人口比例
    epidemic_moveIn = pd.read_csv("D:\\COVID-19\\data\\baidu_migration\\city_move_in_from_WuHan.csv")

    # COVID疫情
    covid_19_history_all = pd.read_csv("D:\\COVID-19\\data\\covid\\COVID_history_city.csv")
    covid_19_history_all = covid_19_history_all[['date', 'cityCode', 'confirmed']]
    covid_19_history_all.columns = ['date', 'id', 'confirmed']

    for i in range(len(dates1)):
        date1 = dates1[i]
        date2 = dates2[i]
        
        rh_temp = rh[['id', date1]]
        rh_temp.columns = ['id', 'rh']
        
        t2m_temp = t2m[['id', date1]]
        t2m_temp.columns = ['id', 't2m']
        
        moveIn_temp = moveIn[['id', date1 + '_moveIn']]
        moveIn_temp.columns = ['id', 'moveIn']

        moveOut_temp = moveOut[['id', date1 + '_moveOut']]
        moveOut_temp.columns = ['id', 'moveOut']

        travel_temp = travel[['id', date1 + '_travel']]
        travel_temp.columns = ['id', 'travel']

        epidemic_moveIn_temp = epidemic_moveIn[['id', '420100_' + date1 + '_moveIn']]
        epidemic_moveIn_temp.columns = ['id', '420100_moveIn']

        covid_19_temp = covid_19_history_all[covid_19_history_all['date'] == date2]
        covid_19_temp = covid_19_temp[['id', 'confirmed']]
        covid_19_temp.columns = ['id', 'confirmed']

        city_feature = pd.merge(china_city_distinct, rh_temp, how='inner', on='id')
        city_feature = pd.merge(city_feature, t2m_temp, how='inner', on='id')
        city_feature = pd.merge(city_feature, moveIn_temp, how='left', on='id')
        city_feature = pd.merge(city_feature, moveOut_temp, how='left', on='id')
        city_feature = pd.merge(city_feature, travel_temp, how='left', on='id')
        city_feature = pd.merge(city_feature, epidemic_moveIn_temp, how='left', on='id')
        city_feature = pd.merge(city_feature, covid_19_temp, how='left', on='id')
        city_feature = city_feature.fillna(0)
        city_feature['date'] = date1

        city_feature_all.append(city_feature)

    city_feature_all = pd.concat(city_feature_all, axis=0)
    city_feature_all.to_csv("./data/city_feature_daily.csv", index=False)


# 各个城市T范围的时序特征和label
def feature_timing(dates1, T=7, split_date = '20200221'):
    city_feature_all = pd.read_csv("./data/city_feature_daily.csv")
    city_feature_timing = []
    dates = []

    for i in range(len(dates1) - T):
        date = dates1[i:i+7]
        dates.append(dates1[i+7])
        
        temp_all = []
        for j in range(len(date)):
            temp = city_feature_all[city_feature_all['date'] == int(date[j])]
            temp = temp[['id', 'rh', 't2m', 'moveIn', 'moveOut', 'travel', '420100_moveIn', 'confirmed']]
            temp.columns = ['id', 'rh_' + str(j+1), 't2m_' + str(j+1), 'moveIn_' + str(j+1), 'moveOut_' + str(j+1), 'travel_' + str(j+1), '420100_moveIn_' + str(j+1), 'confirmed_' + str(j+1)]
            temp_all.append(temp)
        
        city_feature_timing_temp = temp_all[0]
        for k in range(1, len(temp_all)):
            city_feature_timing_temp = pd.merge(city_feature_timing_temp, temp_all[k], on='id', how='inner')
        
        temp_label = city_feature_all[city_feature_all['date'] == int(dates1[i+7])]
        temp_label = temp_label[['id', 'confirmed']]
        temp_label['date'] = dates1[i+7]
        city_feature_timing_temp = pd.merge(city_feature_timing_temp, temp_label, on='id', how='inner')
        city_feature_timing.append(city_feature_timing_temp)

    city_feature_timing = pd.concat(city_feature_timing, axis=0)
    city_feature_timing.to_csv("./data/city_feature_timing.csv", index=False)

    dates = pd.DataFrame(dates)
    dates.columns = ["date_label"]
    
    train_date = dates[dates["date_label"]<split_date]
    test_date = dates[dates["date_label"]>=split_date]

    train_date.to_csv("./data/train_date.csv", index=False)
    test_date.to_csv("./data/test_date.csv", index=False)

# feature normalize
def feature_normalize(split_date = '20200221'):
    city_feature_timing = pd.read_csv("./data/city_feature_timing.csv")
    #city_feature_timing = city_feature_timing[city_feature_timing['id'] == 420900]
 
    train_df = city_feature_timing[city_feature_timing['date']<int(split_date)]
    train_df_y = train_df[['id', 'date', 'confirmed']]
    train_df_x = train_df.drop(['id', 'date', 'confirmed'], axis=1)
    cols = train_df_x.columns
    
    test_df = city_feature_timing[city_feature_timing['date']>=int(split_date)]
    test_df_y = test_df[['id', 'date', 'confirmed']]
    test_df_x = test_df.drop(['id', 'date', 'confirmed'], axis=1)

    scaler = preprocessing.StandardScaler().fit(train_df_x)
    train_df_x = scaler.transform(train_df_x) 
    train_df_x = pd.DataFrame(train_df_x)
    train_df_x.columns = cols
    train_df_x['id'] = list(train_df_y['id'])
    train_df_x['date'] = list(train_df_y['date'])

    test_df_x = scaler.transform(test_df_x)
    test_df_x = pd.DataFrame(test_df_x)
    test_df_x.columns = cols
    test_df_x['id'] = list(test_df_y['id'])
    test_df_x['date'] = list(test_df_y['date'])

    train_df = pd.merge(train_df_y, train_df_x, on=['id', 'date'], how='left')
    test_df = pd.merge(test_df_y, test_df_x, on=['id', 'date'], how='left')

    train_df.to_csv("./data/city_feature_timing_train.csv", index=False)
    test_df.to_csv("./data/city_feature_timing_test.csv", index=False)




# main
if __name__ == '__main__':

    # China location id
    china_location = pd.read_csv("D:\COVID-19\data\china_location_id_2015.csv")
    china_location = china_location[['id', 'location', 'city', 'distinct', 'city_id']]

    china_city = china_location[china_location['city'] == 1]
    china_city = china_city[['id', 'location']]
    print("china city number: " + str(len(china_city)))

    china_distinct = china_location[(china_location['distinct'] == 1) & (china_location['city_id'] == -999)]
    china_distinct = china_distinct[['id', 'location']]
    print("china distinct number: " + str(len(china_distinct)))

    china_city_distinct = pd.concat([china_city, china_distinct])
    china_city_distinct = china_city_distinct[~china_city_distinct['id'].isin(['710000', '810000', '820000', '659006', '659007', '659008', '460300'])]
    print("china city and distinct number: " + str(len(china_city_distinct)))

    # year month day
    years = ['2020']
    months = {'2020': ['01', '02', '03']}
    days = {'01': ['17', '18',
                   '19', '20', '21',
                   '22', '23', '24',
                   '25', '26', '27',
                   '28', '29', '30',
                   '31'],
            '02': ['01', '02', '03',
                   '04', '05', '06',
                   '07', '08', '09',
                   '10', '11', '12',
                   '13', '14', '15',
                   '16', '17', '18',
                   '19', '20', '21',
                   '22', '23', '24',
                   '25', '26', '27',
                   '28', '29'],
            '03': ['01']}
    
    dates1 = []
    dates2 = []
    for year in years:
        for month in months[year]:
            for day in days[month]:
                dates1.append(year + month + day)
                dates2.append(year + '-' + month + '-' + day)
    
    print(len(dates1))
    print(dates1)

    # 各个城市每日的特征
    feature_daily(dates1, dates2, china_city_distinct)

    # 各个城市的时序特征
    feature_timing(dates1, T=7, split_date = '20200221')

    # 各个城市特征归一化
    feature_normalize(split_date = '20200221')
