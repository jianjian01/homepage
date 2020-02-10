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
        netloc = url.netloc
        if not netloc:
            continue
        site = Site.select(lambda x: x.host == netloc).first()
        if site:
            new_site.icon = site.icon
        else:
            Site(host=netloc)
        commit()
        time.sleep(1)


def main():
    """"""
    set_sql_debug(True)
    db.bind(**Config.PONY)
    db.generate_mapping()
    while 1:
        update_icon()
        time.sleep(100)


if __name__ == '__main__':
    main()
