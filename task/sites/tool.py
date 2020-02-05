import bs4
import requests


def bs_get(url, timeout=10):
    resp = requests.get(url, timeout=timeout)
    root = bs4.BeautifulSoup(resp.text, "lxml")
    return root


def insert(conn, domains):
    sql = "REPLACE INTO `site` (`host`, `icon`) VALUES "
    sql = sql + ','.join([" (%s, '') " for _ in domains])

    with conn.cursor() as cursor:
        result = cursor.execute(sql, list(domains))
        print('insert {} domains'.format(result))
    conn.commit()
