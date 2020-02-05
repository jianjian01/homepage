import os
import random
import string
import time
from urllib.parse import urlparse

import favicon as favicon
import requests
from pony.orm import db_session, set_sql_debug, commit

from config import Config
from db import Site, UserSite, db

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Host": "",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15",
    "Accept-Language": "zh-cn",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}


def download(host, icon):
    """下载文件"""
    icon_dir = '/app/static/site/'
    headers['Host'] = host
    print(icon)
    try:
        response = requests.get(icon, stream=True, timeout=5, headers=headers)
        if response.status_code != 200:
            return None
    except Exception as e:
        return None
    icon_id = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(16)])
    with open(os.path.join(icon_dir, '{}.png'.format(icon_id)), 'wb') as image:
        for chunk in response.iter_content(1024):
            image.write(chunk)
    path = os.path.join(icon_dir, '{}.png'.format(icon_id))
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return icon_id


def try_request(host):
    """"""
    if host.startswith('www.'):
        schema_list = ['https://', 'http://']
    else:
        schema_list = ['https://', 'http://', 'http://www.', 'https://www.']
    for schema in schema_list:
        url = schema + host + '/favicon.ico'
        icon_id = download(host, url)
        if icon_id:
            return icon_id


def try_fetch(host):
    """尝试解析首页，找到 icon 的地址"""
    headers['Host'] = host
    if host.startswith('www.'):
        schema_list = ['https://', 'http://']
    else:
        schema_list = ['https://', 'http://', 'http://www.', 'https://www.']

    for schema in schema_list:
        url = schema + host
        try:
            icons = favicon.get(url, headers=headers, timeout=5)
        except Exception as e:
            continue
        return icons
    return ''


@db_session
def get_icon():
    """下载"""
    for site in Site.select(lambda x: not x.icon)[:1000]:
        host = site.host
        icons = try_fetch(host)
        if not icons and host.startswith('www.'):
            icons = try_fetch(host[4:])
        if icons:
            icon = icons[0].url
            icon_id = download(host, icon)
        else:
            # icons = "http://{}/{}".format(host, 'favicon.ico')
            icon_id = try_request(host)

        if not icon_id:
            continue
        site.icon = icon_id
        commit()
        time.sleep(1)


@db_session
def update_icon():
    """更新"""
    for new_site in UserSite.select(lambda x: not x.icon):
        url = urlparse(new_site.url)
        site = Site.select(lambda x: x.host == url.netloc).first()
        if site:
            new_site.icon = site.icon


def main():
    """"""
    set_sql_debug(True)
    db.bind(**Config.PONY)
    db.generate_mapping()
    while 1:
        get_icon()
        time.sleep(10)
        update_icon()


if __name__ == '__main__':
    main()
