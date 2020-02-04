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


@db_session
def get_icon():
    """下载"""
    icon_dir = '../static/site/'

    for site in Site.select(lambda x: not x.icon)[:1000]:
        icons = []
        print(site.host)
        headers['Host'] = site.host
        for url in ['https://', 'http://', 'http://www.', 'https://www.']:
            if url.endswith('www.') and site.host.startswith('www.'):
                continue
            url = url + site.host
            print(url)
            try:
                icons = favicon.get(url, headers=headers, timeout=5)
            except Exception as e:
                print(e)
                continue
            else:
                url = url + site.host
                break

        if icons:
            icon = icons[0].url
        else:
            icon = "{}/{}".format(url, 'favicon.ico')
        try:
            response = requests.get(icon, stream=True, timeout=5)
            if response.status_code != 200:
                continue
        except Exception as e:
            continue
        icon_id = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(16)])
        with open(os.path.join(icon_dir, '{}.png'.format(icon_id)), 'wb') as image:
            for chunk in response.iter_content(1024):
                image.write(chunk)
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
    # update_icon()


if __name__ == '__main__':
    main()
