# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
随机森林的CV散点图
"""

# load package
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
import math
import geopandas as gp

def predict_plot(real_y, prediction_y):

    plt.rcParams['font.sans-serif']=['Times New Roman']#用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False#用来正常显示负号

    ############# 设置图例并且设置图例的字体及大小 #############
    font1 = {'family': 'Times New Roman',
            'weight': 'normal',
            'size': 30,
            }
    
    figsize = 20,16
    figure, ax = plt.subplots(figsize=figsize)
    plt.scatter(real_y, prediction_y, marker='o',c='b', label='', s=80, alpha=0.3, zorder=20)
    plt.plot([-1, 20], [-1, 20], '--', color='black', label='1:1 line', linewidth=2.0)
        
    ############# 设置坐标刻度值的大小以及刻度值的字体 #############
    plt.xlim(-0.5, 5)
    plt.ylim(-0.5, 5)
    plt.tick_params(labelsize=30)

    interval = [0.30, 1.04, 2.00, 3.00, 4.00, 5.00]
    label = [10**(i) for i in range(len(interval))]
    plt.xticks(interval, label, rotation=0)
    plt.yticks(interval, label, rotation=0)
    
    plt.xlabel('CCCs', font1)
    plt.ylabel('CCCsE', font1)

    # x，y轴设置显示刻度一致
    ax = plt.gca()
    ax.set_aspect(1)
    
    plt.savefig('./picture/GWR_CV.eps', dpi=400)
    plt.show()

# main
if __name__ == '__main__':
    #df = gp.GeoDataFrame.from_file("./result/COVID_rf.shp")
    df = gp.GeoDataFrame.from_file("./result/COVID_gwr.shp")
    df = df[['confirmed', 'predict']]
    temp = df['predict'].to_list()
    temp = [math.log(i+1, 10) for i in temp]
    df.loc[:, 'predictLog'] = temp

    temp = df['confirmed'].to_list()
    temp = [math.log(i+1, 10) for i in temp]
    df.loc[:, 'confirmedLog'] = temp


    print(max(df['confirmedLog'].to_list()))
    print(max(df['predictLog'].to_list()))
    predict_plot(df['confirmedLog'].to_list(), df['predictLog'].to_list())
