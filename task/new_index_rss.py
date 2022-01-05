import logging
import time
from datetime import datetime, timedelta

import feedparser
import pymysql
import requests
from dateutil.parser import parse

from config import Config


def parser(rss_id, text):
    """解析内容"""
    feed = feedparser.parse(text)
    data = []
    for item in feed.entries:
        item_link = item.get('link', '')
        item_title = item.get('title', '')
        # item_ID 是 主键，不能缺失，如果找不到，就用其他的代替
        for key in ['id', 'guid', 'link']:
            item_id = item.get(key, '')
            if item_id:
                break
        if not item_id:
            continue
        pub_date = datetime.utcnow() - timedelta(days=7)
        for key in ['published_parsed', 'pubDate', 'published', 'updated_parsed', 'updated']:
            struct_time = item.get(key, None)
            if not struct_time:
                continue
            try:
                pub_date = parse(struct_time)
                break
            except Exception:
                pass
        data.append([
            rss_id,
            item_id[:255],
            item_title,
            item_link[:255],
            pub_date
        ])

    return data


SQL = "INSERT INTO page (`rss`, `page_id`, `title`, `link`, `publish_date`) " \
      " values (%s, %s, %s, %s, %s) AS alias" \
      " ON DUPLICATE KEY UPDATE title=alias.title, link=alias.link"


def main():
    """
    获取 rss 链接
    :return:
    """
    conf = Config()
    conf.PONY.pop('provider', '')
    conn = pymysql.connect(**conf.PONY)
    logging.info("query database")
    session = requests.Session()
    with conn.cursor() as cursor:
        cursor.execute("select id, link from rss order by rand()")
        rows = cursor.fetchall()
    for rss_id, rss_url in rows:
        a = time.time()
        response = session.get(rss_url, timeout=2000)
        content = response.text
        data = parser(rss_id, content)
        b = time.time()
        print(b - a)
        print(data)
        with conn.cursor() as cursor:
            cursor.executemany(SQL, data)
        conn.commit()
        c = time.time()
        print(c - b)


if __name__ == '__main__':
    while 1:
        start = datetime.utcnow()
        main()
        end = datetime.utcnow()
        logging.info("execute: {} - {}".format(start, end))
        duration = end - start
        if duration < timedelta(hours=0.5):
            logging.info("sleep for a while")
            time.sleep(600 - duration.seconds)
