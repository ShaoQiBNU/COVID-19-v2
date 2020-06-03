# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
区县级每日0：00~23：00的t2m数据

对每日t2m数据求均值，得到每日的t2m值，

计算2020-1-1~2020-3-31时间范围内的平均t2m、最大t2m和最小t2m

设置管控日期 2020-1-26
计算2020-1-1~2020-1-26时间范围内的平均t2m、最大t2m和最小t2m
计算2020-1-26~2020-3-31时间范围内的平均t2m、最大t2m和最小t2m
"""

# load package
import pandas as pd

# 区县级rh数据统计
def distinct_statistics(years, months, days, times, t2m, pac_class_id, control_date):
    cols = list(t2m)
    for year in years:
        for month in months[year]:
            for day in days[month]:
                col = []
                for time in times:
                    if 't2m' + '_' + year + month + day + '_' + time in cols:
                        col.append('t2m' + '_' + year + month + day + '_' + time)

                t2m_temp = t2m[col]
                # 按行求和
                pac_class_id[year + month + day] = t2m_temp.apply(lambda x: x.mean(), axis=1)

    pac_class_id.to_csv("./data/ECMWF/zonal_statistics/city_t2m_day.csv", index=False)

    distinct_t2m = pac_class_id[['id']].copy()

    # 只保留特征值
    pac_class_id = pac_class_id.iloc[:, 2::]

    # 管控日期之前
    pac_class_id_before = pac_class_id.loc[:, pac_class_id.columns.values <= control_date]

    # 管控日期之后
    pac_class_id_after = pac_class_id.loc[:, pac_class_id.columns.values > control_date]

    # 整个时间段
    distinct_t2m.loc[:, 't2m_mean'] = pac_class_id.apply(lambda x: x.mean(), axis=1).to_list()
    distinct_t2m.loc[:, 't2m_max'] = pac_class_id.apply(lambda x: x.max(), axis=1).to_list()
    distinct_t2m.loc[:, 't2m_min'] = pac_class_id.apply(lambda x: x.min(), axis=1).to_list()

    # 管控日期之前
    distinct_t2m.loc[:, 't2m_mean_before'] = pac_class_id_before.apply(lambda x: x.mean(), axis=1).to_list()
    distinct_t2m.loc[:, 't2m_max_before'] = pac_class_id_before.apply(lambda x: x.max(), axis=1).to_list()
    distinct_t2m.loc[:, 't2m_min_before'] = pac_class_id_before.apply(lambda x: x.min(), axis=1).to_list()

    # 管控日期之后
    distinct_t2m.loc[:, 't2m_mean_after'] = pac_class_id_after.apply(lambda x: x.mean(), axis=1).to_list()
    distinct_t2m.loc[:, 't2m_max_after'] = pac_class_id_after.apply(lambda x: x.max(), axis=1).to_list()
    distinct_t2m.loc[:, 't2m_min_after'] = pac_class_id_after.apply(lambda x: x.min(), axis=1).to_list()

    # 输出
    distinct_t2m.to_csv("./data/ECMWF/zonal_statistics/city_t2m_final.csv", index=False)


# main
if __name__ == '__main__':

    t2m = pd.read_csv("./data/ECMWF/zonal_statistics/city_t2m.csv", sep=',')

    pac_class_id = t2m[['id']].copy()

    # year month day times
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
    times = [
        '0000', '0100', '0200',
        '0300', '0400', '0500',
        '0600', '0700', '0800',
        '0900', '1000', '1100',
        '1200', '1300', '1400',
        '1500', '1600', '1700',
        '1800', '1900', '2000',
        '2100', '2200', '2300',
    ]

    control_date = '20200125'

    distinct_statistics(years, months, days, times, t2m, pac_class_id, control_date)