# -*- coding: utf-8 -*-
# @Author  : Qi Shao

"""
从今日头条APP的疫情地图获取疫情数据：省级，地级市，区县级

数据清洗内容主要包括：

1. 行政编码和命名清洗

以中国民政部2015的县级及以上行政编码为准：http://www.mca.gov.cn/article/sj/tjbz/a/2015/201706011127.html
对数据进行清洗，校正错误编码；个别地方如经开区、高新区等等，已经手工写了规则做了转换，有些找不到对应区县，作了去除

2. 去除境外来源数据

3. 去除未公布来源数据

4. 去除外来人口数据

5. 某些城市没有区县级的数据，将城市数据放入区县级里
"""


# load package
import pandas as pd
import urllib.request
import json


# data url
url = "https://i.snssdk.com/forum/ncov_data/?activeWidget=1&data_type=%5B2%2C4%5D"
with urllib.request.urlopen(url) as f:
    data = json.loads(f.read().decode('utf-8'))
    data = json.loads(data['ncov_nation_data'])
    data = data['provinces']

# China location id
china_location = pd.read_csv("../data/china_location_id_2015.csv", sep=',')

# 校正id集合
correction_id = {'公主岭220000': 220381, '梅河口220000': 220581, '崇明310000': 310230, '省十里丰监狱330000': 330803,
                 '开州500000': 500234, '梁平500000': 500228, 	'武隆500000': 500232, 	'韩城610000': 610581, '抚宁区130300': 130306,
                 '海港区130300': 130302, '北戴河区130300': 130304, '卢龙县130300': 130324, '崇礼区130700': 130733, '万全区130700': 130729,
                 '平城区140200': 140203, '云冈区140200': 140202, '潞州区140400': 140411, '杨家杖子经济开发区211400': 211402, '南票区211400': 211404,
                 '连山区211400': 211402, '兴城市211400': 211481, '龙港区211400': 211403, '江北新区320100': 320111, '惠山区320200': 320206,
                 '锡山区320200': 320205, '滨湖区320200': 320211, '新吴区320200': 320214, '江阴市320200': 320281, '宜兴市320200': 320282,
                 '梁溪区320200': 320213, '经开区320400': 320412, '工业园区320500': 320506, '高新区320500': 320505, '生态文旅区320800': 320803,
                 '白马湖农场320800': 320803, '靖江市321200': 321282, '姜堰区321200': 321204, '高港区32120': 321203, '泰兴市321200': 321283,
                 '海陵区321200': 321202, '兴化市321200': 321281, '钱塘新区330100': 330104, '东钱湖330200': 330212, '杭州湾新区330200': 330282,
                 '龙港市330300': 330327, '瓯江口产业集聚区330300': 330305, '吴兴区330500': 330502, '德清县330500': 330521, '南浔区330500': 330503,
                 '长兴县330500': 330522, '新站区340100': 340102, '高新区340100': 340104, '经开区340300': 340303, '高新区340300': 340304, '开发区341200': 341202,
                 '市高新区341600': 341602, '湄洲湾北岸350300': 350305, '高新区360100': 	360111, '红谷滩新区360100': 360102, '经开区360100': 360111,
                 '武功山风景名胜区360300': 360323, '柴桑区360400': 360421, '庐山西海管委会360400': 36040, '庐山市360400': 360402, '高新区360500': 360502,
                 '仙女湖区360500': 360502, '即墨区370200': 370282, '东城区411000':	411002, '示范区411600': 411602, '东湖开发区420100': 420111, '东湖风景区420100': 420106,
                 '武当山特区420300': 420381, '高新区420600': 420602, '东津新区420600': 420607, '京山市420800': 420821, '漳河新区420800': 420802, '屈家岭管理区420800': 420821,
                 '中心城区42100': 421002, '高新区421300': 421303, '大洪山镇421300': 421321, '云龙示范区430200': 430204, '南湖新区430600': 430602, '屈原管理区430600': 430624,
                 '高新区430900': 430903, '资阳区430900': 430902, '金洞431100': 431121, '龙华区440300': 440306, '光明区440300': 440306, '坪山区440300': 440307, '大鹏新区440300': 440307,
                 '香洲区440400': 440402, '金湾区440400': 440404, '横琴新区440400': 440402, '斗门区440400': 440403, '高新区440400': 440404, '高栏港区440400': 440404, '大亚湾区441300': 441303,
                 '海陵区441700': 441702, '郫都区510100': 510124, '简阳市510100': 512081, '安州区510700': 510724, '高新区510700': 510703, '市河东新区510900': 510903, '沾益区530300': 530328,
                 '高新区610100': 610113, '经开区610100': 610112, '高新区610300': 610302, '恒口示范区610900': 610902, '永登县620100': 620121, '榆中县620100': 620123, '皋兰县620100': 620122,
                 '安宁区620100': 620105, '麦积区620500': 620503, '秦州区620500': 620502, '张家川县620500': 620525, '清水县620500': 620521, '陇西县621100': 621122, '通渭县621100': 621121,
                 '渭源县621100': 621123, '礼县621200': 621226, '合作市623000': 623001,

                 '长安镇441900': 441900119, '大岭山镇441900': 441900118, '南城街道441900': 441900004, '大朗镇441900': 441900113, '塘厦镇441900': 441900116, '常平镇441900': 441900110,
                 '虎门镇441900': 441900121, '松山湖管委会441900': 441900401, '沙田镇441900': 441900123, '道滘镇441900': 441900124, '莞城街道441900': 441900006, '厚街镇441900': 441900122,
                 '寮步镇441900': 441900111, '横沥镇441900': 441900106,
                 '东城街道441900': 441900003, '黄江镇441900': 441900114, '石碣镇441900': 441900101, '高埗镇441900': 441900129, '石排镇441900': 441900104, '茶山镇441900': 441900103,
                 '望牛墩镇441900': 441900127, '东坑镇441900': 441900109, '企石镇441900': 441900105, '桥头镇441900': 441900107, '石龙镇441900': 441900102, '凤岗镇441900': 441900117,

                 '黄圃镇442000': 442000101, '石岐区街道442000': 442000001, '火炬开发区街道442000': 442000003, '沙溪镇442000': 442000106, '东区街道442000': 442000002, '坦洲镇442000': 442000107,
                 '东升镇442000': 442000104, '横栏镇442000': 442000110, '民众镇442000': 442000102, '南区街道442000': 442000005,
                 '西区街道442000': 442000004, '东凤镇442000': 442000103, '三角镇442000': 442000109, '阜沙镇442000': 442000112, '三乡镇442000': 442000114, '板芙镇442000': 442000115,
                 }



# 省级数据
def save_province(data, china_location):
    province = []
    for i in range(len(data)):
        temp = data[i]
        province_id = int(temp['id'])*10000

        # 累计确诊人数
        province_confirmedNum = temp['confirmedNum']

        # 累计死亡人数
        province_deathsNum = temp['deathsNum']

        # 累计治愈人数
        province_curesNum = temp['curesNum']

        province.append([province_id, province_confirmedNum, province_deathsNum, province_curesNum])

    province = pd.DataFrame(province)
    province.columns = ['province_id', 'province_confirmedNum', 'province_deathsNum', 'province_curesNum']


    china_province = china_location.loc[china_location['province'] == 1, ['id', 'location']]
    china_province.columns = ['province_id', 'province_name']
    print("china province num: " + str(len(china_province)))

    province = pd.merge(china_province, province, how='inner', on="province_id")
    province.to_csv("../data/COVID19_province.csv", index=False)


# 地级市数据
def save_city(data, china_location):
    city = []

    for i in range(len(data)):
        temp = data[i]
        province_id = int(temp['id']) * 10000

        if province_id in [110000, 120000, 310000, 500000]:
            # 累计确诊人数
            province_confirmedNum = temp['confirmedNum']

            # 累计死亡人数
            province_deathsNum = temp['deathsNum']

            # 累计治愈人数
            province_curesNum = temp['curesNum']

            city.append([province_id, province_confirmedNum, province_deathsNum, province_curesNum, province_id])

    china_province = china_location.loc[china_location['province'] == 1, ['id', 'location']]
    china_province.columns = ['province_id', 'province_name']
    province_id = china_province['province_id'].to_list()

    china_city = china_location.loc[china_location['city'] == 1, ['id', 'location', 'province_id']]
    china_city.columns = ['city_id', 'city_name', 'province_id']
    city_ids = china_city['city_id'].to_list()
    print("china city num: " + str(len(china_city)))

    china_distinct = china_location.loc[china_location['distinct'] == 1, ['id', 'location']]
    distinct_ids = china_distinct['id'].to_list()

    print("app COVID-19 data don't exist in any city!")

    for id in province_id:
        # data url
        province_url = "https://i.snssdk.com/toutiao/normandy/pneumonia_trending/district_stat/?local_id=" + str(id).ljust(6, '0')
        with urllib.request.urlopen(province_url) as f:
            province_data = json.loads(f.read().decode('utf-8'))
            province_data = province_data['data']['list']

        for i in range(len(province_data)):
            temp = province_data[i]
            city_id = temp['local_id']
            city_name = temp['name']

            # 累计确诊人数
            city_confirmedNum = temp['confirmed_count']

            # 累计死亡人数
            city_deathsNum = temp['death_count']

            # 累计治愈人数
            city_curesNum = temp['cured_count']

            if city_name+str(city_id) in correction_id.keys():
                city_id = correction_id[city_name+str(city_id)]

            if city_id in city_ids:
                city.append([city_id, city_confirmedNum, city_deathsNum, city_curesNum, id])
            else:
                if city_id not in distinct_ids:
                    print(city_id, city_name, city_confirmedNum, city_deathsNum, city_curesNum, id)

    city = pd.DataFrame(city)
    city.columns = ['city_id', 'city_confirmedNum', 'city_deathsNum', 'city_curesNum', 'province_id']
    city = pd.merge(city, china_city, how='left', on=["city_id"])
    city = city.fillna(value=0)
    city[['city_confirmedNum', 'city_deathsNum', 'city_curesNum']] = city[['city_confirmedNum', 'city_deathsNum', 'city_curesNum']].astype(int)
    city.to_csv("../data/COVID19_city.csv", index=False)
    print("COVID-19 data city num: " + str(len(city)))
    return city


# 区县级数据
def save_distinct(china_location, city):

    # 东莞市 中山市 台湾省 香港 澳门
    city_id_substitute = [441900, 442000, 710000, 810000, 820000]
    distinct = []

    china_province = china_location.loc[china_location['province'] == 1, ['id', 'location']]
    china_province.columns = ['province_id', 'province_name']
    province_id = china_province['province_id'].to_list()

    china_city = china_location.loc[china_location['city'] == 1, ['id', 'location', 'province_id']]
    china_city.columns = ['city_id', 'city_name', 'province_id']
    city_ids = china_city['city_id'].to_list()

    china_distinct = china_location.loc[china_location['distinct'] == 1, ['id', 'location', 'province_id', 'city_id']]
    china_distinct.columns = ['distinct_id', 'distinct_name', 'province_id', 'city_id']
    distinct_ids = china_distinct['distinct_id'].to_list()
    print("china distinct num: " + str(len(china_distinct)))

    print("app COVID-19 data don't exist in any distinct! From province")
    for id in province_id:
        # data url
        province_url = "https://i.snssdk.com/toutiao/normandy/pneumonia_trending/district_stat/?local_id=" + str(
            id).ljust(6, '0')
        with urllib.request.urlopen(province_url) as f:
            province_data = json.loads(f.read().decode('utf-8'))
            province_data = province_data['data']['list']

        for i in range(len(province_data)):
            temp = province_data[i]
            distinct_id = temp['local_id']
            distinct_name = temp['name']

            # 累计确诊人数
            distinct_confirmedNum = temp['confirmed_count'] if temp['confirmed_count'] > 0 else 0

            # 累计死亡人数
            distinct_deathsNum = temp['death_count'] if temp['death_count'] > 0 else 0

            # 累计治愈人数
            distinct_curesNum = temp['cured_count'] if temp['cured_count'] > 0 else 0

            if distinct_name+str(id) in correction_id.keys():
                distinct_id = correction_id[distinct_name+str(id)]

            if distinct_id in distinct_ids:
                distinct.append([distinct_id, distinct_confirmedNum, distinct_deathsNum, distinct_curesNum])
            else:
                if distinct_id in province_id:
                    print(distinct_id, distinct_name, distinct_confirmedNum, distinct_deathsNum, distinct_curesNum, id)

    print("app COVID-19 data don't exist in any distinct! From city")
    for id in city_ids:
        # data url
        city_url = "https://i.snssdk.com/toutiao/normandy/pneumonia_trending/district_stat/?local_id=" + str(
            id).ljust(6, '0')
        with urllib.request.urlopen(city_url) as f:
            city_data = json.loads(f.read().decode('utf-8'))
            city_data = city_data['data']['list']

        if len(city_data) == 0:
            city_id_substitute.append(id)

        for i in range(len(city_data)):
            temp = city_data[i]
            distinct_id = temp['local_id']
            distinct_name = temp['name']

            # 累计确诊人数
            distinct_confirmedNum = temp['confirmed_count'] if temp['confirmed_count'] > 0 else 0

            # 累计死亡人数
            distinct_deathsNum = temp['death_count'] if temp['death_count'] > 0 else 0

            # 累计治愈人数
            distinct_curesNum = temp['cured_count'] if temp['cured_count'] > 0 else 0

            if distinct_name+str(id) in correction_id.keys():
                distinct_id = correction_id[distinct_name+str(id)]

            if distinct_id in distinct_ids:
                distinct.append([distinct_id, distinct_confirmedNum, distinct_deathsNum, distinct_curesNum])
            else:
                print(distinct_id, distinct_name, str(distinct_name) + str(id), distinct_confirmedNum, distinct_deathsNum, distinct_curesNum, id)

    distinct = pd.DataFrame(distinct)
    distinct.columns = ['id', 'confirmedNum', 'deathsNum', 'curesNum']

    # 个别区县级数据安装校正编码集合校正后，需要按照id聚合统计
    distinct = distinct.groupby('id').agg(sum).reset_index()

    city_substitute = city[city['city_id'].isin(city_id_substitute)]
    city_substitute = city_substitute[city_substitute['city_confirmedNum'] > 0]
    city_substitute = city_substitute[['city_id', 'city_confirmedNum', 'city_deathsNum', 'city_curesNum']]
    city_substitute.columns = ['id', 'confirmedNum', 'deathsNum', 'curesNum']

    print("The following cities don't contains distinct data!")
    print(city_substitute['id'])
    distinct = pd.concat([distinct, city_substitute])

    distinct = pd.merge(distinct, china_location[['id', 'location']], how='left', on='id')

    '''

    china_distinct = pd.merge(china_distinct, china_city, how='left', on=["city_id", 'province_id'])
    china_distinct = china_distinct.fillna(value=-1)

    china_distinct = pd.merge(china_distinct, china_province, how='left', on=['province_id'])
    china_distinct = china_distinct.fillna(value=-1)

    distinct = pd.merge(china_distinct, distinct, how='left', on=["distinct_id"])

    print("COVID-19 data city num: " + str(len(distinct)))

    distinct = distinct.fillna(value=0)
    distinct[['distinct_confirmedNum', 'distinct_deathsNum', 'distinct_curesNum']] = distinct[
        ['distinct_confirmedNum', 'distinct_deathsNum', 'distinct_curesNum']].astype(int)

    distinct = distinct[['distinct_id', 'distinct_name', 'distinct_confirmedNum', 'distinct_deathsNum', 'distinct_curesNum',
                         'city_id', 'city_name', 'province_id', 'province_name']]
    
    '''

    distinct.to_csv("../data/COVID19_distinct.csv", index=False)


# province data
print("start get province data")
save_province(data, china_location)
print("end!")


# city data
print("start get city data")
city = save_city(data, china_location)
print("end!")


# dictinct data
print("start get distinct data")
save_distinct(china_location, city)
print("end!")
