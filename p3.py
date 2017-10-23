import requests
from pprint import pprint
import os
import time


URL = 'http://www.toutiao.com/search_content/?offset=20&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&cur_tab=1'


def download_page(url):
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    data = requests.get(url, headers=head).json()
    return data


def get_pic_url(post):
    if not post.get('article_url'):
        return
    title = post.get('title')
    images = post.get('image_detail')
    if images:
        pic_url = [p['url'] for p in images]
        return {'title': title, 'pic_url': pic_url}


def download_pic(post_dict):
    if not post_dict:
        return
    post_title = post_dict['title']
    print('开始爬取：'+post_title)
    pic_url_list = post_dict['pic_url']
    for pic_url in pic_url_list:
        pic_title = pic_url.split('/')[-1]
        if not os.path.exists('街拍图/'+post_title):
            os.makedirs('街拍图/'+post_title)
        with open('街拍图/'+post_title+'/'+pic_title+'.jpg', 'wb') as fl:
            pic = requests.get(pic_url).content
            fl.write(pic)
        time.sleep(0.5)

if __name__ == '__main__':
    data = download_page(URL).get('data')
    if data:
        for post in data:
            post_dict = get_pic_url(post)
            download_pic(post_dict)