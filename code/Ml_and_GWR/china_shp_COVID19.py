# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
将中国2015的区县级、地级市、省级的shp文件加入COVID-19疫情属性
"""

import geopandas
import pandas as pd
import math

'''
""" 
对中国2015的区县级shp文件加上 cityId 和 provinceId
"""

# 2015 China distinct shp
path = '/Users/shaoqi/Desktop/COVID-19/shp/china_all_8_dissolve.shp'
shp_df = geopandas.GeoDataFrame.from_file(path)
shp_df.rename(columns={'PAC': 'id'}, inplace=True)

print(shp_df)

# 2015 China location id
location_df = pd.read_csv('../data/china_location_id_2015.csv', sep=',')
location_df = location_df[['id', 'location', 'province', 'city', 'distinct', 'city_id', 'province_id']]


location_df.loc[(location_df['distinct']==1) & (location_df['city_id']==-999), 'city_id'] = location_df[(location_df['distinct']==1) & (location_df['city_id']==-999)]['id']
location_df = location_df[['id', 'location', 'city_id', 'province_id']]

shp_df = pd.merge(shp_df, location_df, how='left', on='id')
shp_df.to_file("../shp/china_distinct.shp", encoding='utf-8')
print(len(shp_df))
'''

'''
""" 
输出中国的直辖市、地级市和省直辖区县
"""
# 2015 China distinct shp
path = '../shp/china_all_8_dissolve.shp'
shp_df = geopandas.GeoDataFrame.from_file(path)
shp_df.rename(columns={'PAC': 'id'}, inplace=True)


# 2015 China location id
location_df = pd.read_csv('../data/china_location_id_2015.csv', sep=',')
location_df = location_df[['id', 'location', 'province', 'city', 'distinct', 'city_id', 'province_id']]


city = location_df[location_df['city']==1]

distinct = location_df[(location_df['distinct']==1) & (location_df['city_id']==-999)]

city_distinct = pd.concat([city, distinct])
city_distinct = city_distinct[['id', 'location', 'city', 'distinct', 'province_id']]
city_distinct.to_csv("../data/china_city_distinct_2018.csv", index=False)
'''

'''
""" 
输出中国的直辖市、地级市和省直辖区县
"""
# 2015 China distinct shp
df = pd.read_csv('../data/ECMWF/zonal_statistics/pac_class_city_id.csv')

id1 = df['id'].to_list()
print(len(df))


city_distinct = pd.read_csv("../data/china_city_distinct_2018.csv")
print(len(city_distinct))

id2 = city_distinct['id'].to_list()

print(set(id2).difference(set(id1)))
'''


df_all = pd.read_csv("./output/COVID_final.csv")


df = df_all[['id','npp','location',
'rh_mean','rh_max','rh_min',
't2m_mean','t2m_max','t2m_min',
'confirmed','cured','dead',
'moveIn_index_mean','moveIn_index_max','moveIn_index_min',
'moveOut_index_mean','moveOut_index_max','moveOut_index_min',
'travel_index_mean','travel_index_max','travel_index_min',
'420100_moveIn_mean','420100_moveIn_max','420100_moveIn_min',
'confirmed_log','cured_log','dead_log']]

df.columns = ['id','npp','location',
'rhMean','rhMax','rhMin',
't2mMean','t2mMax','t2mMin',
'confirmed','cured','dead',
'moveInMean','moveInMax','moveInMin',
'moveOutMean','moveOutMax','moveOutMin',
'travelMean','travelMax','travelMin',
'WuhanMean','WuhanMax','WuhanMin',
'confirmLog','curedLog','deadLog']


df_before = df_all[['id','npp','location',
'rh_mean_before','rh_max_before','rh_min_before',
't2m_mean_before','t2m_max_before','t2m_min_before',
'confirmed_before','cured_before','dead_before',
'moveIn_index_mean_before','moveIn_index_max_before','moveIn_index_min_before',
'moveOut_index_mean_before','moveOut_index_max_before','moveOut_index_min_before',
'travel_index_mean_before','travel_index_max_before','travel_index_min_before',
'420100_moveIn_mean_before','420100_moveIn_max_before','420100_moveIn_min_before',
'confirmed_before_log','cured_before_log','dead_before_log']]


df_before.columns = ['id','npp','location',
'rhMean','rhMax','rhMin',
't2mMean','t2mMax','t2mMin',
'confirmed','cured','dead',
'moveInMean','moveInMax','moveInMin',
'moveOutMean','moveOutMax','moveOutMin',
'travelMean','travelMax','travelMin',
'WuhanMean','WuhanMax','WuhanMin',
'confirmLog','curedLog','deadLog']


df_after = df_all[['id','npp','location',
'rh_mean_after','rh_max_after','rh_min_after',
't2m_mean_after','t2m_max_after','t2m_min_after',
'confirmed_after','cured_after','dead_after',
'moveIn_index_mean_after','moveIn_index_max_after','moveIn_index_min_after',
'moveOut_index_mean_after','moveOut_index_max_after','moveOut_index_min_after',
'travel_index_mean_after','travel_index_max_after','travel_index_min_after',
'420100_moveIn_mean_after','420100_moveIn_max_after','420100_moveIn_min_after',
'confirmed_after_log','cured_after_log','dead_after_log']]

df_after.columns = ['id','npp','location',
'rhMean','rhMax','rhMin',
't2mMean','t2mMax','t2mMin',
'confirmed','cured','dead',
'moveInMean','moveInMax','moveInMin',
'moveOutMean','moveOutMax','moveOutMin',
'travelMean','travelMax','travelMin',
'WuhanMean','WuhanMax','WuhanMin',
'confirmLog','curedLog','deadLog']


# 2015 China city shp
path = './shp/china_city_UTM.shp'
shp_city = geopandas.GeoDataFrame.from_file(path)
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

aaaaa



# 2015 China distinct shp
path = '../shp/china_distinct.shp'
shp_distinct = geopandas.GeoDataFrame.from_file(path)

# 2015 China city shp
path = '../shp/china_city.shp'
shp_city = geopandas.GeoDataFrame.from_file(path)
shp_city.rename(columns={'cityId': 'id', 'cityName': 'location'}, inplace=True)
print(len(shp_city))



aaaaa

# 2015 China province shp
path = '../shp/china_province.shp'
shp_province = geopandas.GeoDataFrame.from_file(path)
shp_province.rename(columns={'proId': 'id', 'proName': 'location'}, inplace=True)


# COVID19 distinct
china_distinct = pd.read_csv("../data/COVID19_distinct.csv", sep=',')
china_distinct = china_distinct[['distinct_id', 'distinct_name', 'distinct_confirmedNum']]
china_distinct.columns = ['id', 'name', 'confirmedNum']

# COVID19 city
china_city = pd.read_csv("../data/COVID19_city.csv", sep=',')
china_city = china_city[['city_id', 'city_name', 'city_confirmedNum']]
china_city.columns = ['id', 'name', 'confirmedNum']

# COVID19 province
china_province = pd.read_csv("../data/COVID19_province.csv", sep=',')
china_province = china_province[['province_id', 'province_name', 'province_confirmedNum']]
china_province.columns = ['id', 'name', 'confirmedNum']

# merge
china = pd.concat([china_city, china_distinct])
shp_distinct = pd.merge(shp_distinct, china, how='left', on='id')
shp_distinct = shp_distinct.fillna(value=0)
shp_distinct.to_file("../shp/china_distinct_COVID19.shp", encoding='utf-8')

# display level
print("distinct display level:")
num = shp_distinct['confirmedNum'].to_list()

level = [5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 90, 150, 250, 500, 1000, 3000, 6000, 9000]
for i in range(1, len(level)):
    res=0
    for j in num:
        if j<=level[i] and j>level[i-1]:
            res+=1
    print(level[i-1], level[i], res)

# merge
shp_city = pd.merge(shp_city, china_city, how='left', on='id')
shp_city = shp_city.fillna(value=0)
shp_city.to_file("../shp/china_city_COVID19.shp", encoding='utf-8')

# display level
print("city display level:")
num = shp_city['confirmedNum'].to_list()

level = [5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100, 150, 200, 500, 1000, 5000, 60000]
for i in range(1, len(level)):
    res = 0
    for j in num:
        if j <= level[i] and j > level[i - 1]:
            res += 1
    print(level[i - 1], level[i], res)

# merge
shp_province = pd.merge(shp_province, china_province, how='left', on='id')
shp_province = shp_province.fillna(value=0)
shp_province.to_file("../shp/china_province_COVID19.shp", encoding='utf-8')

# display level
print("province display level:")
num = shp_province['confirmedNum'].to_list()

level = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 700000]
for i in range(1, len(level)):
    res = 0
    for j in num:
        if j <= level[i] and j > level[i - 1]:
            res += 1
    print(level[i - 1], level[i], res)


