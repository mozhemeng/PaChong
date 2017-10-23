import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sqlite3
import re


URL = 'http://tianqi.moji.com/'


def download_page(url):
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    data = requests.get(url, headers=head).text
    return data


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    weather_info = soup.find('div', attrs={'class': 'wrap clearfix wea_info'}).find('div', attrs={'class': 'left'})
    # 空气质量指数
    wea_alert = weather_info.find('div', attrs={'class': 'wea_alert clearfix'})
    aqi = wea_alert.em.getText()
    aqi_num, aqi_str = tuple(aqi.split(' '))
    # 温度，天气，更新时间
    wea_weather = weather_info.find('div', attrs={'class': 'wea_weather clearfix'})
    temp = wea_weather.em.getText()
    weather = wea_weather.b.getText()
    refresh = wea_weather.strong.getText()
    refresh_time = re.findall(r'\d{2}:\d{2}', refresh)
    if refresh_time:
        refresh_time = int(refresh_time[0].split(':')[0])
    else:
        refresh_time = -1
    # 湿度，风向，限行
    wea_about = weather_info.find('div', attrs={'class': 'wea_about clearfix'})
    hum = wea_about.span.getText()
    wind = wea_about.em.getText()
    ban = wea_about.b.getText()
    # tips
    wea_tips = weather_info.find('div', attrs={'class': 'wea_tips clearfix'})
    tips = wea_tips.em.getText()
    # 日期
    today = datetime.now().date().strftime('%Y-%m-%d')
    # 构建字典
    wea_dict = {'today': today, 'aqi_num': aqi_num, 'aqi_str': aqi_str, 'temp': temp, 'weather': weather,
                'refresh': refresh, 'hum': hum, 'wind': wind, 'ban': ban, 'tips': tips, 'refresh_time': refresh_time}
    print(wea_dict)
    return wea_dict


def save2sql(d):
    sql = "insert into weather_hour (day, hour, temp, wea, hum, wind, aqi_num, aqi_str, tips) " \
          "VALUES (?,?,?,?,?,?,?,?,?);"
    sql_value = (d['today'], d['refresh_time'], d['temp'], d['weather'],
                 d['hum'], d['wind'], d['aqi_num'], d['aqi_str'], d['tips'])
    conn = sqlite3.connect('weather_db.db')
    cursor = conn.cursor()
    cursor.execute(sql, sql_value)
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # 请求页面
    html_doc = download_page(URL)
    # 分析页面，组合成天气情况字典
    wea_dict = parse_html(html_doc)
    # 存至数据库
    save2sql(wea_dict)
