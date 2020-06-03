# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
AkShare平台 https://akshare.readthedocs.io/zh_CN/latest/data/event/event.html

世界历史疫情数据，提取中国地级市的历史疫情数据
"""

# load package
import akshare as ak
import time
import pandas as pd
import geopandas as gp


def get_china_history_data(province_id, city_distinct_id):
    # get data
    covid_19_history_df = ak.covid_19_history()
    covid_19_history_df = covid_19_history_df[covid_19_history_df['country'] == '中国']
    covid_19_history_china = covid_19_history_df[(covid_19_history_df['province'] == '') & (covid_19_history_df['city'] == '')]
    covid_19_history_china = covid_19_history_china[['date', 'confirmed', 'cured', 'dead']]
    covid_19_history_china.to_csv("./output/COVID_china.csv", index=False)

    covid_19_history_df = covid_19_history_df[['date', 'province', 'provinceCode', 'city', 'cityCode',
                                               'confirmed', 'cured', 'dead']]
    # 去除nan
    covid_19_history_df = covid_19_history_df.drop(covid_19_history_df[covid_19_history_df['province'] == ''].index)

    # province
    covid_19_history_province = covid_19_history_df[covid_19_history_df['city'] == '']
    covid_19_history_province = covid_19_history_province[['date', 'province', 'provinceCode', 'confirmed', 'cured', 'dead']]

    covid_19_history_province[['provinceCode', 'confirmed', 'cured', 'dead']] = \
        covid_19_history_province[['provinceCode', 'confirmed', 'cured', 'dead']].astype(int)

    covid_19_history_province.to_csv("./output/COVID_history_province.csv", index=False)

    # 直辖市
    covid_19_history_province.columns = ['date', 'city', 'cityCode', 'confirmed', 'cured', 'dead']
    covid_19_history_province = covid_19_history_province[covid_19_history_province['cityCode'].isin(province_id)]


    covid_19_history_df = covid_19_history_df[['date', 'city', 'cityCode', 'confirmed', 'cured', 'dead']]


    # correction city 校正错误的city
    correction_id = {'650500': '652200', '540500': '542200'}
    correction_city = covid_19_history_df[covid_19_history_df['cityCode'].isin(correction_id)]
    for id in correction_id.keys():
        correction_city.loc[correction_city['cityCode']==id, 'cityCode'] = correction_id[id]

    correction_city[['cityCode', 'confirmed', 'cured', 'dead']] = \
        correction_city[['cityCode', 'confirmed', 'cured', 'dead']].astype(int)

    # city
    covid_19_history_city = covid_19_history_df[covid_19_history_df['cityCode'].isin(city_distinct_id)]
    covid_19_history_city[['cityCode', 'confirmed', 'cured', 'dead']] = \
        covid_19_history_city[['cityCode', 'confirmed', 'cured', 'dead']].astype(int)


    # 合并 直辖市，地级市
    covid_19_history_all = pd.concat([covid_19_history_province, correction_city, covid_19_history_city])

    #city_distinct_id = [int(i) for i in city_distinct_id]
    #print(set(city_distinct_id).difference(set(covid_19_history_all['cityCode'].to_list())))

    covid_19_history_all.to_csv("./output/COVID_history_city.csv", index=False)


# main
if __name__ == '__main__':

    # China location id
    china_location = pd.read_csv("./data/china_location_id_2015.csv", sep=',')
    china_location = china_location[['id', 'location', 'province', 'city', 'distinct',
                                     'province_id', 'city_id']]

    china_city = china_location[china_location['city'] == 1]
    china_city = china_city[['id', 'location']]
    print("china city number: " + str(len(china_city)))

    china_distinct = china_location[(china_location['distinct'] == 1) & (china_location['city_id'] == -999)]
    china_distinct = china_distinct[['id', 'location']]
    print("china distinct number: " + str(len(china_distinct)))

    china_city_distinct = pd.concat([china_city, china_distinct])
    print("china city and distinct number: " + str(len(china_city_distinct)))


    # get china province and city data
    province_id = ['110000', '310000', '120000', '500000']
    city_distinct_id = china_city_distinct['id'].to_list()
    city_distinct_id = [str(i) for i in city_distinct_id]

    get_china_history_data(province_id, city_distinct_id)

    covid_19_history_all = pd.read_csv("./output/COVID_history_city.csv")



    # 获取累计到2020-1-26的疫情数据
    control_date = '2020-01-25'
    covid_19_history_before = covid_19_history_all[covid_19_history_all['date'] == control_date]
    covid_19_history_before = covid_19_history_before[['cityCode', 'confirmed', 'cured', 'dead']]
    covid_19_history_before.columns = ['id', 'confirmed_before', 'cured_before', 'dead_before']
    print(control_date + ": " + str(len(covid_19_history_before)))


    # 获取累计到今天的疫情数据
    covid_19_history_after = covid_19_history_all[covid_19_history_all['date'] == "2020-03-01"]
    covid_19_history_after = covid_19_history_after[['cityCode', 'confirmed', 'cured', 'dead']]
    covid_19_history_after.columns = ['id', 'confirmed', 'cured', 'dead']
    print("2020-03-01: " + str(len(covid_19_history_after)))

    china_city_distinct = pd.merge(china_city_distinct, covid_19_history_before, how='left', on='id')
    china_city_distinct = pd.merge(china_city_distinct, covid_19_history_after, how='left', on='id')

    china_city_distinct['confirmed_after'] = china_city_distinct['confirmed'] - china_city_distinct['confirmed_before']
    china_city_distinct['cured_after'] = china_city_distinct['cured'] - china_city_distinct['cured_before']
    china_city_distinct['dead_after'] = china_city_distinct['dead'] - china_city_distinct['dead_before']
    china_city_distinct = china_city_distinct.fillna(0)
    china_city_distinct[['confirmed_before', 'cured_before', 'dead_before', 'confirmed', 'cured', 'dead', 'confirmed_after', 'cured_after', 'dead_after']] \
        = china_city_distinct[['confirmed_before', 'cured_before', 'dead_before', 'confirmed', 'cured', 'dead', 'confirmed_after', 'cured_after', 'dead_after']].astype(int)

    china_city_distinct.to_csv("./output/COVID_city_distinct.csv", index=False)


    # 2015 China city shp
    path = './shp/china_city_UTM.shp'
    shp_city = gp.GeoDataFrame.from_file(path)
    shp_city.rename(columns={'city_id': 'id'}, inplace=True)
    print(len(shp_city))

    covid = china_city_distinct[['id', 'confirmed']]
    shp_city_all = pd.merge(shp_city, covid, how='left', on='id')
    shp_city_all = shp_city_all.fillna(0)
    shp_city_all.to_file("./shp/china_COVID19.shp", encoding='utf-8')
    print(len(shp_city_all))

