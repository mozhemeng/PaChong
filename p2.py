import requests
import time
from pyquery import PyQuery as pq
import sqlite3


URL = 'https://hz.zu.anjuke.com/fangyuan/hushu/'


def download_page(url):
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    data = requests.get(url, headers=head).text
    return data


def parse_html(html):
    d = pq(html)
    house_list = d('#list-content div.zu-itemmod')
    l = []
    sql_value = []
    for house_info in house_list.items():
        house = house_info.find('div.zu-info')
        house_name = house.find('h3').text()
        house_details = house.find('p.details-item.tag').text()
        house_address = house.find('address.details-item').text().replace(' ', '')
        house_price = house_info.find('div.zu-side p').text()
        house_all = house_name+ house_details+ house_address+ house_price
        l.append(house_all)
        sql_value.append((house_name, house_details, house_address, house_price))
    next_page = d('div.multi-page').find('a.aNxt')
    if next_page:
        return '\n'.join(l), sql_value, next_page.attr('href')
    return '\n'.join(l), sql_value, None


def main():
    print('开始爬取')
    url = URL
    sql = "insert into rent_info (name, detial, address, price) VALUES (?,?,?,?);"
    with open('house_information.txt', 'w', encoding='utf8') as fl:
        while url:
            print('正在爬取'+url)
            page = download_page(url)
            house_data, sql_value, url = parse_html(page)
            fl.write(house_data)
            # print(house_data)
            cursor.executemany(sql, sql_value)
            time.sleep(1)
    print('爬取结束')


if __name__ == '__main__':
    conn = sqlite3.connect('house_rent_information.db')
    cursor = conn.cursor()
    main()
    cursor.close()
    conn.commit()
    conn.close()