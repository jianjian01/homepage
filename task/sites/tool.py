from datetime import datetime

import bs4
import requests
from pymysql import connect

from config import Config


def bs_get(url, timeout=10):
    resp = requests.get(url, timeout=timeout)
    root = bs4.BeautifulSoup(resp.text, "lxml")
    return root


def conn():
    conf = Config.PONY
    conf.pop('provider', '')
    c = connect(**conf)
    c.autocommit(True)
    return c


def insert_site(conn, domains):
    sql = "REPLACE INTO `site` (`host`, `icon`) VALUES "
    sql = sql + ','.join([" (%s, '') " for _ in domains])

    with conn.cursor() as cursor:
        result = cursor.execute(sql, list(domains))
        print('insert {} domains'.format(result))
    conn.commit()


def insert_usersite(conn, user, website):
    """"""
    sql = "insert into usersite(`name`, `url`, `icon`, `user`, `order`, `create_time`, `status`) values "
    today = datetime.utcnow()
    value_sql = []
    data = []
    for s in website:
        data.append([s[0], s[1], user, today])
        value_sql.append('(%s, %s, "", %s, 500, %s, 1)')
    sql += ', '.join(value_sql)
    new_data = []
    for d in data:
        new_data.extend(d)
    with conn.cursor() as cursor:
        result = cursor.execute(sql, new_data)
        print('insert {} website'.format(result))
    conn.commit()
