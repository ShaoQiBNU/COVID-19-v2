# -*- coding: utf-8 -*-
# @Author  : Qi Shao

import geopandas
import pandas as pd

'''
china_location = pd.read_csv("../data/china_location_id.csv", sep=',')

id = china_location['id'].to_list()

province_id = list(filter(lambda x: x % 10000 == 0, id))
print(len(province_id))

china_location['province'] = 0
china_location.loc[china_location['id'].isin(province_id), 'province'] = 1
print(len(china_location[china_location['id'].isin(province_id)]))


city_id = list(filter(lambda x: x % 10000 != 0 and x % 100 == 0, id))
print(len(city_id))

china_location['city'] = 0
china_location.loc[china_location['id'].isin(city_id), 'city'] = 1
print(len(china_location[china_location['id'].isin(city_id)]))


distinct_id = list(filter(lambda x: x % 10000 != 0 and x % 100 != 0, id))
print(len(distinct_id))

china_location['distinct'] = 0
china_location.loc[china_location['id'].isin(distinct_id), 'distinct'] = 1
print(len(china_location[china_location['id'].isin(distinct_id)]))


china_location['province_id'] = [i//10000*10000 if i//10000*10000 in province_id else -1 for i in id]
china_location['city_id'] = [i//100*100 if i//100*100 in city_id else -1 for i in id]

china_location.to_csv("../data/china_location_id_2015.csv", index=False)

'''

path = '../shp/china_all_dissolve.shp'
shp_df = geopandas.GeoDataFrame.from_file(path)
shp_df = shp_df[['PAC']]

china_location = pd.read_csv("../data/china_location_id.csv", sep=',')

id = china_location['id'].to_list()

ids = shp_df['PAC'].to_list()


df2 = shp_df[~shp_df['PAC'].isin(id)]

df2.to_csv("../output/try.csv", index=False)

path = '../shp/china_all_dissolve.shp'
shp_df = geopandas.GeoDataFrame.from_file(path)
shp_df.rename(columns={'PAC': 'id'}, inplace=True)
shp_df = shp_df[['id']]

china_distinct = pd.read_csv("../data/COVID19_distinct.csv", sep=',')
id = china_distinct['distinct_id'].to_list()

china_city = pd.read_csv("../data/COVID19_city.csv", sep=',')
id.extend(china_city['city_id'].to_list())

china_city = pd.read_csv("../data/COVID19_province.csv", sep=',')
id.extend(china_city['province_id'].to_list())

df2 = shp_df[~shp_df['id'].isin(id)]

df2.to_csv("../output/try.csv", index=False)

