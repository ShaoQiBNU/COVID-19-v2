# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
百度迁徙数据平台：http://qianxi.baidu.com/?from=baiduse

爬取中国每天的城市迁徙link，输出到文件里，文件格式如下：

512000 520200

表示城市520200迁徙到512000，link关系为：520200->512000
"""

# load package
import pandas as pd
import json
import requests
import numpy as np
import time


# city 迁出比例
def city_migration_link(china_city_distinct, years, months, days):

    city_baidu_ids = china_city_distinct['city_baidu_id'].to_list()
    city_link = []
    city_name = china_city_distinct['location'].to_list()

    for year in years:
        for month in months[year]:
            for day in days[month]:
                date = year + month + day

                print(date)

                for id in city_baidu_ids:

                    url = 'http://huiyan.baidu.com/migration/cityrank.jsonp?dt=city&id=' + str(id) + '&type=move_out' + '&date=' + date
                    try:
                        city_data = requests.get(url).content.decode('utf-8')[3:-1]
                        city_data = json.loads(city_data)['data']['list']

                        for i in range(len(city_data)):
                            name = city_data[i]['city_name']
                            if name not in city_name:
                                print(name)
                            city_link.append([china_city_distinct.loc[china_city_distinct['location']==name, ['id']].values[0][0],
                                              china_city_distinct.loc[china_city_distinct['city_baidu_id']==id, ['id']].values[0][0]])
                    except:
                        print(url)

                city_link = pd.DataFrame(city_link)
                city_link.to_csv("./data/covid/covid.cites." + date, index=False, header=None, sep='\t')
                print("end")
# main
if __name__ == '__main__':

    # China location id
    china_location = pd.read_csv("D:\COVID-19\data\china_location_id_2015.csv")
    china_location = china_location[['id', 'location', 'city_baidu_id', 'city', 'distinct', 'city_id']]

    china_city = china_location[china_location['city'] == 1]
    china_city = china_city[['id', 'location', 'city_baidu_id']]
    print("china city number: " + str(len(china_city)))

    china_distinct = china_location[(china_location['distinct'] == 1) & (china_location['city_id'] == -999)]
    china_distinct = china_distinct[['id', 'location', 'city_baidu_id']]
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
    
    # migration link
    city_migration_link(china_city_distinct, years, months, days)

