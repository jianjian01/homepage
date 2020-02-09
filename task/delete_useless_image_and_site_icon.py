import os

from pony.orm import set_sql_debug, raw_sql, commit

from config import Config
from db import Site, db


def delete_images():
    while 1:
        count, loop = 0, 0
        limit = loop * 1000
        offset = 1000
        for site in Site.select(lambda x: x.icon).order_by(raw_sql('rand()')).limit(limit, offset):
            count += 1
            path = os.path.join(Config.ICON_DIR, '{}.png'.format(site.icon))
            if not os.path.exists(path):
                site.icon = ''
        commit()
        if count < 1000:
            break


def delete_site_icon():
    for filename in os.listdir(Config.ICON_DIR):
        path = os.path.join(Config.ICON_DIR, filename)
        if os.path.isdir(path):
            continue
        icon_id = filename[:-4]
        if not Site.select(lambda x: x.icon == icon_id).exists():
            os.remove(path)


def main():
    set_sql_debug(True)
    db.bind(**Config.PONY)
    db.generate_mapping()
    delete_images()
    delete_site_icon()


if __name__ == '__main__':
    main()
