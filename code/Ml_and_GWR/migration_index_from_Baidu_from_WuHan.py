# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
百度迁徙数据平台：http://qianxi.baidu.com/?from=baiduse
爬取武汉迁入各个城市的比例和武汉的迁入和迁出迁徙指数，并计算乘积
计算累计值、最大值和最小值
"""

# load package
import pandas as pd
import json
import requests
import numpy as np
import time
import os


# city 迁出、迁入迁徙规模指数
def move_migration_index(id):
    url = 'http://huiyan.baidu.com/migration/historycurve.jsonp?dt=city&id=' + str(id) + '&type=move_out'
    moveOut = requests.get(url).content.decode('utf-8')[3:-1]
    moveOut = json.loads(moveOut)['data']['list']

    url = 'http://huiyan.baidu.com/migration/historycurve.jsonp?dt=city&id=' + str(id) + '&type=move_in'
    moveIn = requests.get(url).content.decode('utf-8')[3:-1]
    moveIn = json.loads(moveIn)['data']['list']

    return moveOut, moveIn


# city 迁出比例
def epidemic_migration(china_city, china_distinct, epidemicIds, years, months, days):

    china_city_name = china_city['name'].to_list()
    china_distinct_name = china_distinct['name'].to_list()
    distinct_name = set()

    china_city_moveIn = china_city.copy()
    china_city_moveOut = china_city.copy()

    china_distinct_moveIn = china_distinct.copy()
    china_distinct_moveOut = china_distinct.copy()


    for id in epidemicIds:
        moveOut, moveIn = move_migration_index(id)

        for year in years:
            for month in months[year]:
                for day in days:

                    date = year + month + day
                    url = 'http://huiyan.baidu.com/migration/cityrank.jsonp?dt=city&id=' + str(id) + '&type=move_out' + '&date=' + date
                    city_data = requests.get(url).content.decode('utf-8')[3:-1]
                    city_data = json.loads(city_data)['data']['list']

                    if len(city_data)>0:
                        china_city_moveOut[str(id) + '_' + date + '_moveOut'] = 0
                        china_city_moveIn[str(id) + '_' + date + '_moveIn'] = 0

                        china_distinct_moveOut[str(id) + '_' + date + '_moveOut'] = 0
                        china_distinct_moveIn[str(id) + '_' + date + '_moveIn'] = 0

                        for i in range(len(city_data)):
                            name = city_data[i]['city_name']
                            value = city_data[i]['value']

                            if name in china_city_name:
                                china_city_moveOut.loc[china_city_moveOut['name'] == name, str(id) + '_' + date + '_moveOut'] = moveOut[date] * value / 100
                                china_city_moveIn.loc[china_city_moveIn['name'] == name, str(id) + '_' + date + '_moveIn'] = moveIn[date] * value / 100

                            elif name in china_distinct_name:
                                distinct_name.add(name)
                                china_distinct_moveOut.loc[china_distinct_moveOut['name'] == name, str(id) + '_' + date + '_moveOut'] = moveOut[date] * value / 100
                                china_distinct_moveIn.loc[china_distinct_moveIn['name'] == name, str(id) + '_' + date + '_moveIn'] = moveIn[date] * value / 100
                            else:
                                print(name)

                        china_city_moveOut.loc[china_city_moveOut['city_baidu_id'] == id, str(id) + '_' + date + '_moveOut'] = moveOut[date]
                        china_city_moveIn.loc[china_city_moveIn['city_baidu_id'] == id, str(id) + '_' + date + '_moveIn'] = moveIn[date]

                    else:
                        print(url)

    china_distinct_moveOut = china_distinct_moveOut[china_distinct_moveOut['name'].isin(list(distinct_name))]
    china_distinct_moveIn = china_distinct_moveIn[china_distinct_moveIn['name'].isin(list(distinct_name))]

    return china_city_moveOut, china_city_moveIn, china_distinct_moveOut, china_distinct_moveIn


# city 迁出比例
def epidemic_migration_proportion(china_city_distinct, epidemicIds, years, months, days):

    china_city_distinct_name = china_city_distinct['name'].to_list()
    china_city_distinct_moveIn_from_Wuhan = china_city_distinct.copy()

    for id in epidemicIds:

        moveOut, moveIn = move_migration_index(id)

        for year in years:
            for month in months[year]:
                for day in days[month]:

                    date = year + month + day
                    url = 'http://huiyan.baidu.com/migration/cityrank.jsonp?dt=city&id=' + str(id) + '&type=move_out' + '&date=' + date
                    city_data = requests.get(url).content.decode('utf-8')[3:-1]
                    city_data = json.loads(city_data)['data']['list']

                    if len(city_data)>0:
                        china_city_distinct_moveIn_from_Wuhan[str(id) + '_' + date + '_moveIn'] = 0

                        for i in range(len(city_data)):
                            name = city_data[i]['city_name']
                            value = city_data[i]['value'] 

                            if name in china_city_distinct_name:
                                china_city_distinct_moveIn_from_Wuhan.loc[china_city_distinct_moveIn_from_Wuhan['name'] == name, str(id) + '_' + date + '_moveIn'] = moveOut[date] * value

                            else:
                                print(name)

                        china_city_distinct_moveIn_from_Wuhan.loc[china_city_distinct_moveIn_from_Wuhan['city_baidu_id'] == id, str(id) + '_' + date + '_moveIn'] = moveOut[date] * 100

                    else:
                        print(url)

    return china_city_distinct_moveIn_from_Wuhan


# main
if __name__ == '__main__':

    #获取当前目录的绝对路径
    path = os.path.realpath(os.curdir)

    # China location id
    china_location = pd.read_csv("./data/china_location_id_2015.csv")

    # china city
    china_city = china_location.loc[china_location['city'] == 1, ['city_baidu_id', 'location', 'id']]
    china_city.columns = ['city_baidu_id', 'name', 'id']
    print("china city num: " + str(len(china_city)))

    # china distinct
    china_distinct = china_location.loc[(china_location['distinct'] == 1) & (china_location['city_id'] == -999),
                                        ['city_baidu_id', 'location', 'id']]
    china_distinct.columns = ['city_baidu_id', 'name', 'id']

    print("china distinct num: " + str(len(china_distinct)))

    china_city_distinct = pd.concat([china_city, china_distinct])
    print("china city and distinct number: " + str(len(china_city_distinct)))


    # epidemic id 疫情灾区id，暂定武汉
    epidemicIds = [420100]
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

    control_date = '20200125'

    # migration
    china_city_distinct_moveIn_from_Wuhan = epidemic_migration_proportion(china_city_distinct, epidemicIds, years, months, days)
    china_city_distinct_moveIn_from_Wuhan.to_csv("./data/baidu_migration/city_move_in_from_WuHan.csv", index=False)

    # city migration In sum
    epidemic_moveIn_sum = china_city_distinct_moveIn_from_Wuhan[['id', 'name', 'city_baidu_id']].copy()
    epidemic_moveIn = china_city_distinct_moveIn_from_Wuhan.iloc[:, 3::]

    for id in epidemicIds:
        epidemic_moveIn_city = epidemic_moveIn.loc[:,
                               (epidemic_moveIn.columns.values <= str(id) + '_' + time.strftime("%Y%m%d") + '_moveIn') &
                               (epidemic_moveIn.columns.values >= str(id) + '_' + '20200101_moveIn')]

        epidemic_moveIn_before = epidemic_moveIn_city.loc[:,
                                 epidemic_moveIn_city.columns.values <= str(id) + '_' + control_date + '_moveIn']
        epidemic_moveIn_after = epidemic_moveIn_city.loc[:,
                                epidemic_moveIn_city.columns.values > str(id) + '_' + control_date + '_moveIn']

        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_mean'] = epidemic_moveIn_city.apply(lambda x: x.mean(), axis=1)
        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_mean_before'] = epidemic_moveIn_before.apply(lambda x: x.mean(), axis=1)
        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_mean_after'] = epidemic_moveIn_after.apply(lambda x: x.mean(), axis=1)

        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_max'] = epidemic_moveIn_city.apply(lambda x: x.max(), axis=1)
        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_max_before'] = epidemic_moveIn_before.apply(lambda x: x.max(), axis=1)
        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_max_after'] = epidemic_moveIn_after.apply(lambda x: x.max(), axis=1)

        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_min'] = epidemic_moveIn_city.apply(lambda x: x.min(), axis=1)
        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_min_before'] = epidemic_moveIn_before.apply(lambda x: x.min(), axis=1)
        epidemic_moveIn_sum.loc[:, str(id) + '_moveIn_min_after'] = epidemic_moveIn_after.apply(lambda x: x.min(), axis=1)

    epidemic_moveIn_sum.to_csv("./data/baidu_migration/city_move_in_from_WuHan_sum.csv", index=False)

    '''
    # migration
    china_city_moveOut, china_city_moveIn, china_distinct_moveOut, china_distinct_moveIn = epidemic_migration(china_city, china_distinct, epidemicIds, years, months, days)

    # city migration In
    epidemic_moveOut = pd.concat([china_city_moveOut, china_distinct_moveOut])
    epidemic_moveOut.to_csv("../data/baidu_migration/city_migration_out_from_WuHan.csv", index=False)

    # city migration In sum
    epidemic_moveOut_sum = epidemic_moveOut[['city_baidu_id', 'name', 'province_id']]
    epidemic_moveOut = epidemic_moveOut.iloc[:, 3::]

    for id in epidemicIds:
        epidemic_moveOut_city = epidemic_moveOut.loc[:,
                               (epidemic_moveOut.columns.values <= str(id) + '_' + time.strftime("%Y%m%d") + '_moveIn') &
                               (epidemic_moveOut.columns.values >= str(id) + '_' + '20200101_moveIn')]

        epidemic_moveOut_before = epidemic_moveOut_city.loc[:, epidemic_moveOut_city.columns.values <= str(id) + '_' + control_date + '_moveOut']
        epidemic_moveOut_after = epidemic_moveOut_city.loc[:, epidemic_moveOut_city.columns.values > str(id) + '_' + control_date + '_moveOut']

        epidemic_moveOut_sum[str(id) + '_moveOut_sum'] = epidemic_moveOut_city.apply(lambda x: x.sum(), axis=1)
        epidemic_moveOut_sum[str(id) + '_moveOut_sum_before'] = epidemic_moveOut_before.apply(lambda x: x.sum(), axis=1)
        epidemic_moveOut_sum[str(id) + '_moveOut_sum_after'] = epidemic_moveOut_after.apply(lambda x: x.sum(), axis=1)

    epidemic_moveOut_sum.to_csv("../data/baidu_migration/city_migration_out_from_WuHan_sum.csv", index=False)


    # city migration In
    epidemic_moveIn = pd.concat([china_city_moveIn, china_distinct_moveIn])
    epidemic_moveIn.to_csv("../data/baidu_migration/city_migration_in_from_WuHan.csv", index=False)

    # city migration In sum
    epidemic_moveIn_sum = epidemic_moveIn[['city_baidu_id', 'name', 'province_id']]
    epidemic_moveIn = epidemic_moveIn.iloc[:, 3::]

    for id in epidemicIds:
        epidemic_moveIn_city = epidemic_moveIn.loc[:, (epidemic_moveIn.columns.values <= str(id) + '_' + time.strftime("%Y%m%d") + '_moveIn') &
                                                        (epidemic_moveIn.columns.values >= str(id) + '_' + '20200101_moveIn')]

        epidemic_moveIn_before = epidemic_moveIn_city.loc[:, epidemic_moveIn_city.columns.values <= str(id) + '_' + control_date + '_moveIn']
        epidemic_moveIn_after = epidemic_moveIn_city.loc[:, epidemic_moveIn_city.columns.values > str(id) + '_' + control_date + '_moveIn']

        epidemic_moveIn_sum[str(id) + '_moveIn_sum'] = epidemic_moveIn_city.apply(lambda x: x.sum(), axis=1)
        epidemic_moveIn_sum[str(id) + '_moveIn_sum_before'] = epidemic_moveIn_before.apply(lambda x: x.sum(), axis=1)
        epidemic_moveIn_sum[str(id) + '_moveIn_sum_after'] = epidemic_moveIn_after.apply(lambda x: x.sum(), axis=1)

    epidemic_moveIn_sum.to_csv("../data/baidu_migration/city_migration_in_from_WuHan_sum.csv", index=False)
    '''

