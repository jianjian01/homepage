import time
from urllib.parse import urlparse

from pony.orm import db_session, set_sql_debug, commit

from config import Config
from db import Site, UserSite, db


@db_session
def update_icon():
    """更新"""
    for new_site in UserSite.select(lambda x: not x.icon):
        url = urlparse(new_site.url)
        site = Site.select(lambda x: x.host == url.netloc).first()
        if site:
            new_site.icon = site.icon
        else:
            Site(host=url.netloc)
        commit()


def main():
    """"""
    set_sql_debug(True)
    db.bind(**Config.PONY)
    db.generate_mapping()
    while 1:
        update_icon()


if __name__ == '__main__':
    main()
