import asyncio
from urllib.parse import urlparse

import pymysql
from pony.orm import commit, db_session

from config import Config
from db import db, Site, UserSite, User
from task.download_site_icon_async import run

urls = [
    'https://www.lu.com/',
    'https://jr.mi.com/',
    'http://www.fund123.cn/',

    'https://www.topys.cn/',
    'http://www.xici.net',
    'https://mail.163.com/',
]


@db_session
def main():
    """"""
    # db.bind(**Config.PONY)
    # db.generate_mapping()
    download_list = []
    insert_list = []
    user = User.select(lambda x: x.id == 1).first()
    for url in urls:
        us = urlparse(url)
        site = Site.select(lambda x: x.host == us.netloc).first()
        if not site:
            site = Site(host=us.netloc, icon='')
        icon = site.icon

        if not icon:
            download_list.append([site.id, site.host])
        else:
            us = UserSite.select(lambda x: x.url == url and x.user == user).first()
            if us:
                us.icon = icon
            else:
                us = UserSite(name=site.host, url=url, user=user, icon=icon)
            print('{} {}'.format(url, icon))
    commit()
    if download_list:
        conn = pymysql.connect(**Config.PONY)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(loop, download_list, conn))
        loop.close()
        conn.close()


if __name__ == '__main__':
    main()
