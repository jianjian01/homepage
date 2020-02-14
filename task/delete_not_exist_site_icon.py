import os
import time

from pony.orm import set_sql_debug, raw_sql, commit, db_session

from config import Config
from db import Site, db


@db_session
def delete_site_icon():
    while 1:
        count, loop = 0, 0
        limit = 1000
        offset = loop * 1000
        for site in Site.select(lambda x: x.icon).limit(limit, offset):
            count += 1
            path = os.path.join(Config.ICON_DIR, '{}.png'.format(site.icon))
            if not os.path.exists(path):
                print(site.icon)
                site.icon = ''
        if count < 1000:
            break


def main():
    set_sql_debug(True)
    db.bind(**Config.PONY)
    db.generate_mapping()
    delete_site_icon()


if __name__ == '__main__':
    main()
