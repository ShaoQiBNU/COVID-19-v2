# COVID-19

## COVID-19中国各行政级数据获取

```shell
# 今日头条APP的疫情地图获取疫情数据：省级，地级市，区县级，输出 /data/COVID19_province.csv，/data/COVID19_city.csv，/data/COVID19_distinct.csv

cd code

python COVID19_from_TouTiao.py
```

### 数据说明

```shell
中国2015年省级、地级市、区县级行政编码
/data/china_location_id.csv
/data/china_location_id_2015.csv

省级疫情数据
/data/COVID19_province.csv   

地级市疫情数据
/data/COVID19_city.csv

区县级疫情数据
/data/COVID19_distinct.csv
```


### 2015中国区县级shp文件COVID-19属性加入

```shell
# 将上面COVID-19中国各行政级数据获取数据加进2015年中国区县级shp文件的属性表里

cd code

python china_shp_COVID19.py
```

#### 数据说明

```shell
中国2015年区县级shp文件
/shp/china_distinct.shp

中国2015年地级市shp文件
/shp/china_city.shp  

中国2015年省级shp文件
/shp/china_province.shp  
  


中国2015年区县级shp文件（含有COVID19累计确诊人数属性）
/shp/china_distinct_COVID19.shp

中国2015年地级市shp文件（含有COVID19累计确诊人数属性）
/shp/china_city_COVID19.shp

中国2015年省级shp文件（含有COVID19累计确诊人数属性）
/shp/china_province_COVID19.shp



中国2015年shp文件（含有COVID19累计确诊人数属性）mxd文件——软件是ArcMap10.2
/shp/COVID19_2015_COVID19.mxd

中国2015年区县级COVID19空间自相关分析——软件是GeoDa
```

## ECMWF ERA5数据获取及处理

### ERA5数据获取，python下载，netCDF格式
```shell
cd code

# 2m temperature
python t2m_from_ECMWF_ERA5.py

# 1000hPa relative humidity
python rh_from_ECMWF_ERA5.py
```

### 数据说明

```shell
中国 2m temperature
/data/ECMWF/t2m/nc

t2m_20200101_0000.nc   2020年1月1日 00:00  netCDF  2m temperature


中国 1000hPa relative humidity
/data/ECMWF/rh/nc

rh_20200101_0000.nc   2020年1月1日 00:00  netCDF  1000hPa relative humidity
```

### ERA5数据处理，IDL处理成envi standard
```shell
cd code

# 2m temperature  1000hPa relative humidity ---- IDL

netCDFToTiff.pro

```

### 数据说明

```shell
中国 2m temperature
/data/ECMWF/t2m/tif

t2m_20200101_0000.tif   2020年1月1日 00:00  envi standard  2m temperature


中国 1000hPa relative humidity
/data/ECMWF/rh/tif

rh_20200101_0000.tif   2020年1月1日 00:00  envi standard  1000hPa relative humidity
```

### ERA5数据分区统计
```shell
cd code

# 2m temperature  1000hPa relative humidity ---- IDL

zonal_statistics.pro

```

### 数据说明

```shell
中国区县级 2m temperature 分区统计
/data/ECMWF/zonal_statistics/distinct_t2m.csv

中国区县级 1000hPa relative humidity 分区统计
/data/ECMWF/zonal_statistics/distinct_rh.csv


中国地级市 2m temperature 分区统计
/data/ECMWF/zonal_statistics/city_t2m.csv

中国地级市 1000hPa relative humidity 分区统计
/data/ECMWF/zonal_statistics/city_rh.csv


辅助文件：

中国区县级分类文件
/data/ECMWF/zonal_statistics

class_distinct_id.tif  class_distinct_id.hdr


class_id.tif的每个像元值代表id，id与区县行政编码的对应文件
pac_class_distinct_id.csv


中国地级市分类文件
/data/ECMWF/zonal_statistics

class_city_id.tif  class_city_id.hdr


class_id.tif的每个像元值代表id，id与区县行政编码的对应文件
pac_class_city_id.csv

```

### ERA5数据累计值统计
```shell
cd code

# 2m temperature  1000hPa relative humidity

python rh_statistics.py

python t2m_statistics.py
```

### 数据说明

```shell
中国区县级 2m temperature 1000hPa relative humidity 统计

/data/ECMWF/zonal_statistics/distinct_t2m_final.csv
/data/ECMWF/zonal_statistics/distinct_rh_final.csv


中国地级市 2m temperature 1000hPa relative humidity 统计

/data/ECMWF/zonal_statistics/city_t2m_final.csv
/data/ECMWF/zonal_statistics/city_rh_final.csv
```

## 夜光数据NPP/VIIRS

```shell script

cd code

# 夜光统计 ---- IDL

zonal_statistics_light.pro

```

### 数据说明

```shell

中国地级市夜光分区统计结果

/data/npp/city_npp.csv

```

## 百度迁徙数据获取

```shell
cd code

# 城市迁入迁徙规模指数、迁出迁徙规模指数和城内出行强度
python migration_index_from_Baidu.py

# 疫情城市迁入其他城市迁入迁徙规模指数、迁出迁徙规模指数和城内出行强度
python migration_index_from_Baidu_from_WuHan.py
```

### 数据说明

```shell

# 城市迁入迁徙规模指数、迁出迁徙规模指数和城内出行强度
/data/baidu_migration/city_migration.csv


# 疫情城市迁入迁徙规模指数、迁出迁徙规模指数与比例的乘积
/data/baidu_migration/city_migration_from_WuHan.csv
```