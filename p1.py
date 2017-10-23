import requests
import time
from pyquery import PyQuery as pq


URL = 'https://movie.douban.com/top250'


def download_page(url):
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    data = requests.get(url, headers=head).text
    return data


def parse_html(html):
    d = pq(html)
    movie_li_list = d('ol.grid_view li')
    movie_name_list = []
    for movie_li in movie_li_list.items():
        movie_name = movie_li.find('div.hd span.title').text().replace('\xa0', '')
        movie_name_list.append(movie_name)
    next_page = d('span.next').find('a')
    if next_page:
        next_page_url = URL + next_page.attr('href')
        return movie_name_list, next_page_url
    return movie_name_list, None


def main():
    url = URL
    while url:
        page = download_page(url)
        movie, url = parse_html(page)
        print(movie)
        time.sleep(0.5)


if __name__ == '__main__':
    main()