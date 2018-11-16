#!/usr/bin/env python3
# -*- coding:utf-8 -*-
""" Get Weather """

import csv
import requests
from datetime import datetime


TOKEN = ''
CITY_CSV = 'city.csv'
SKYCON = {
    "CLEAR_DAY": "晴天",
    "CLEAR_NIGHT": "晴夜",
    "PARTLY_CLOUDY_DAY": "多云",
    "PARTLY_CLOUDY_NIGHT": "多云",
    "CLOUDY": "阴",
    "RAIN": "雨",
    "SNOW": "雪",
    "WIND": "风",
    "HAZE": "雾霾沙尘"}
WIND_SPEED = {
    0: ["1",     "无风", "烟直上"],
    1: ["1-5",   "软风", "烟稍斜"],
    2: ["6-11",  "轻风", "树叶响"],
    3: ["12-19", "微风", "树枝晃"],
    4: ["20-28", "和风", "灰尘起"],
    5: ["29-38", "清风", "水起波"],
    6: ["39-49", "强风", "大树摇"],
    7: ["50-61", "劲风", "步难行"],
    8: ["62-74", "大风", "树枝折"],
    9: ["75-88", "烈风", "烟囱毁"]}


def get_location(province, city=None, zone=None):
    with open(CITY_CSV, 'r') as csvfile:
        cityread = csv.reader(csvfile)
        flag = 0
        ret = None
        for i in cityread:
            if province in i[0]:
                flag += 1
                if flag == 1:
                    ret = i
                if city and city in i[1]:
                    if zone:
                        if zone in i[2]:
                            ret = i
                        else:
                            continue
                    else:
                        ret = i
                else:
                    continue
            assert ret, "Not found %s. Please enter again" % province
            return ret


def get_wind_speed(speed):
    if speed <= 1:
        return WIND_SPEED.get(0)
    else:
       WIND_SPEED.pop(0)
       for k,v in WIND_SPEED.items():
            start, end = v[0].split('-')
            if int(start) <= int(speed) <= int(end):
                v.insert(0,k)
                return v


def get_realtime_weather(province, city=None, zone=None):
    """
    get_weather(province, city=None, zone=None)
    """
    LOCATION = get_location(province, city, zone)
    coordinate = ','.join(LOCATION[-2:])
    API = 'https://api.caiyunapp.com/v2/%s/%s/realtime.json?unit=metric:v2' % (TOKEN, coordinate)
    weather = requests.get(API)
    weather = weather.json()
    
    server_time = float(weather.get('server_time'))
    server_time = datetime.fromtimestamp(server_time)
    speed = weather.get('result').get('wind').get('speed')
    skycon = SKYCON.get(weather.get('result').get('skycon'))
    temperature =  weather.get('result').get('temperature')
    ultraviolet = weather.get('result').get('ultraviolet').get('desc')
    region = LOCATION[:2]
    speed_msg = get_wind_speed(speed)

    result = """
    %s
    北京时间: %s
    当前天气: %s
     紫外线 : %s
    当前气温: %s℃ 
    当前风速: %skm/h, %s级, %s""" % (','.join(region), server_time, skycon,
                                    ultraviolet, temperature,
                                    speed, speed_msg[0],
                                    ','.join(speed_msg[-2:]))

    return result


def get_forecast_weather(province, city=None, zone=None):
    """
    get_weather(province, city=None, zone=None)
    """
    LOCATION = get_location(province, city, zone)
    coordinate = ','.join(LOCATION[-2:])
    API = 'https://api.caiyunapp.com/v2/G4GV25ceb9iD9g0P/%s/forecast.json?unit=metric:v2' % coordinate
    weather = requests.get(API)
    weather = weather.json()

    server_time = float(weather.get('server_time'))
    server_time = datetime.fromtimestamp(server_time)
    daily = weather.get('result').get('daily')
    speed = daily.get('wind')[0].get('avg').get('speed')
    skycon = SKYCON.get(daily.get('skycon')[0].get('value'))
    temperature =  daily.get('temperature')[0]
    temp_avg = temperature.get('avg')
    temp_min = temperature.get('min')
    temp_max = temperature.get('max')
    ultraviolet = daily.get('ultraviolet')[0].get('desc')
    pm25 = daily.get('pm25')[0].get('max')
    sun = daily.get('astro')[0]
    sun_set = sun.get('sunset').get('time')
    sun_rise = sun.get('sunrise').get('time')
    region = LOCATION[:2]
    speed_msg = get_wind_speed(speed)

    result = """北京时间: %s
%s
明天天气概况
  日出: %s
  日落: %s
  天气: %s
  pm2.5 : %s
 紫外线 : %s
  气温: 最高 %s℃ 最低 %s℃ 平均 %s℃
  风速: %skm/h, %s级, %s""" % (server_time, ','.join(region), sun_rise, sun_set, skycon, pm25,
                               ultraviolet, temp_max, temp_min, temp_avg,
                               speed, speed_msg[0],
                               ','.join(speed_msg[-2:]))

    return result

if __name__ == '__main__':
    the_weather = get_realtime_weather('北京', '朝阳')
    print(the_weather)
