import requests
from bs4 import BeautifulSoup
from datetime import datetime
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
    # 限行
    wea_about = weather_info.find('div', attrs={'class': 'wea_about clearfix'})
    ban = wea_about.b.getText()
    # tips
    wea_tips = weather_info.find('div', attrs={'class': 'wea_tips clearfix'})
    tips = wea_tips.em.getText()
    # 日期
    date = datetime.now().date().strftime('%Y-%m-%d')

    weather_today_info = soup.find_all('div', attrs={'class': 'wrap clearfix'})[1].\
        find('div', attrs={'class': 'forecast clearfix'})
    # 今日情况
    today = weather_today_info.find('ul', attrs={'class': 'days clearfix'}).find_all('li')
    # 天气
    weather = today[1].getText().strip()
    # 温度
    temp = today[2].getText()
    temp_num = re.findall(r'\d+', temp)
    if len(temp_num) == 2:
        temp_low = temp_num[0]
        temp_high = temp_num[1]
    else:
        temp_low = 0
        temp_high = 0
    # 风向
    wind_from = today[3].em.getText()
    wind_num = today[3].b.getText()
    # 空气质量
    aqi = today[4].strong.getText().strip()
    aqi_num, aqi_str = tuple(aqi.split(' '))
    # 构建字典
    wea_dict = {'today': date, 'aqi_num': aqi_num, 'aqi_str': aqi_str, 'temp_low': temp_low, 'temp_high': temp_high,
                'weather': weather, 'wind_from': wind_from, 'wind_num': wind_num, 'ban': ban, 'tips': tips}
    return wea_dict


def create_text(d):
    text = "今天是{d[today]}, 天气{d[weather]}, 气温{d[temp_low]}到{d[temp_high]}摄氏度，" \
           "风向为{d[wind_from]}，{d[wind_num]}，空气质量{d[aqi_num]}，{d[aqi_str]}, {d[ban]}，今天{d[tips]}".format(d=d)
    print(text)
    return text


def text2voice(text):
    url = 'http://tts.baidu.com/text2audio?idx=1&tex={0}&cuid=baidu_speech_' \
          'demo&cod=2&lan=zh&ctp=1&pdt=1&spd=4&per=4&vol=5&pit=5'.format(text)
    return url


def download_voice(d,url):
    with open('天气语音/' + d['today'] + '.mp3', 'wb') as fl:
        vic = requests.get(url).content
        fl.write(vic)


def save2sql(d):
    sql = "insert into weather_day (day, wea, temp_low, temp_high, wind_from, wind_num, aqi_num, aqi_str, ban, tips)" \
          " VALUES (?,?,?,?,?,?,?,?,?,?);"
    sql_value = (d['today'], d['weather'], d['temp_low'], d['temp_high'],
                 d['wind_from'], d['wind_num'], d['aqi_num'], d['aqi_str'], d['ban'], d['tips'])
    conn = sqlite3.connect('weather_db.db')
    with conn as cur:
        cur.execute(sql, sql_value)
    # cursor = conn.cursor()
    # cursor.execute(sql, sql_value)
    # cursor.close()
    # conn.commit()
    # conn.close()


if __name__ == '__main__':
    # 请求页面
    html_doc = download_page(URL)
    # 分析页面，组合成天气情况字典
    wea_dict = parse_html(html_doc)
    # 行程播报字符创
    voice_text = create_text(wea_dict)
    # 行程播报语音url
    voice_url = text2voice(voice_text)
    # 下载语音
    download_voice(wea_dict, voice_url)
    # 存至数据库
    save2sql(wea_dict)
