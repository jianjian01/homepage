from urllib.parse import urlparse

import bs4

import requests
from pymysql import connect

from config import Config


def insert(urls):
    conf = Config.PONY
    conf.pop('provider', '')
    conn = connect(**conf)

    sql = "REPLACE INTO `site` (`host`, `icon`) VALUES "
    sql = sql + ','.join([" (%s, '') ".format(url) for url in urls])

    with conn.cursor() as cursor:
        cursor.execute(sql, list(urls))
    conn.commit()
    conn.close()


def query_alexa(url):
    resp = requests.get('https://alexa.chinaz.com' + url, timeout=10)
    root = bs4.BeautifulSoup(resp.text, "lxml")
    urls = set()
    dom = root.find_all('ul', class_='rowlist')
    if not dom:
        return
    dom = dom[0]
    for d in dom.find_all('a'):
        href = d.get('href')
        if 'chinaz.com' in href:
            continue
        urls.add(urlparse(href).netloc)

    insert(urls)


def main():
    url = 'https://alexa.chinaz.com/Global/'
    resp = requests.get(url, timeout=10)
    root = bs4.BeautifulSoup(resp.text, "lxml")
    urls = set()
    dom = root.find_all("div", class_="dqWrap-Show")[0]
    for d in dom.find_all('a'):
        href = d.get('href')
        urls.add(href)
    print('urls count {}'.format(len(urls)))

    for url in urls:
        print(url)
        for i in range(20):
            if i == 0:
                new_url = url
            else:
                index = '_' + str(i + 1) + '.html'
                new_url = url[:-5] + index
            try:
                query_alexa(new_url)
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    main()
