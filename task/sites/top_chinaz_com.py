import bs4
import requests
from pymysql import connect

from config import Config
from task.sites.tool import bs_get, insert


def urll(url):
    if url.startswith("http"):
        return url
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return 'https://top.chinaz.com' + url
    return url


def prefetch(url):
    """查看一共有多少页"""
    resp = requests.get(url, timeout=10)
    root = bs4.BeautifulSoup(resp.text, "lxml")
    page = root.find_all('div', class_='ListPageWrap')[0]
    max_value = 0
    for a_dom in page.find_all('a'):
        text = a_dom.string
        if text.isdigit() and int(text) > max_value:
            max_value = int(text)
    if max_value > 500:
        max_value = 500
    return max_value


def query_top(url):
    """"""
    root = bs_get(url)
    content = root.find_all('ul', class_='listCentent')[0]
    domains = set()
    for page in content.find_all('span', class_='col-gray'):
        domains.add(page.string)
    return domains


def main():
    url = 'https://top.chinaz.com/'
    resp = requests.get(url, timeout=10)
    root = bs4.BeautifulSoup(resp.text, "lxml")
    urls = {d.get('href') for d in root.find_all("a", class_="TNMI-SubItem")
            if d.get('href').startswith('//top.chinaz.com')}
    print('urls count {}'.format(len(urls)))

    conf = Config.PONY
    conf.pop('provider', '')
    conn = connect(**conf)
    conn.autocommit(True)

    for url in urls:
        url = urll(url)
        print(url)
        page_count = prefetch(url)
        for i in range(page_count):
            if i == 0:
                new_url = url
            else:
                index = '_' + str(i + 1) + '.html'
                new_url = url[:-5] + index
            try:
                domains = query_top(new_url)
                if domains:
                    insert(conn, domains)
            except Exception as e:
                print(e)
                continue
    conn.close()


if __name__ == '__main__':
    main()
