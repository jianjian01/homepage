import logging
import time
from datetime import datetime, timedelta

import cchardet
import feedparser
import pymysql
import pytz
import requests
import urllib3
from dateutil.parser import parse

from config import Config

urllib3.disable_warnings()
utc = pytz.UTC

logging.getLogger().setLevel(logging.DEBUG)

logging.info("start")
def parser(rss_id, text):
    """解析内容"""
    feed = feedparser.parse(text)
    data = []
    old_date = datetime.today() - timedelta(days=30)
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
        if pub_date.replace(tzinfo=None) < old_date.replace(tzinfo=None):
            continue
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
    results = []
    for rss_id, rss_url in rows:
        try:
            response = session.get(rss_url, timeout=2000, verify=False)
        except Exception:
            continue
        coding = cchardet.detect(response.content)['encoding']
        data = ''
        if coding:
            try:
                data = parser(rss_id, response.content.decode(coding))
            except Exception:
                pass
        if not data:
            data = parser(rss_id, response.text)
        if data:
            results.extend(data)
    with conn.cursor() as cursor:
        cursor.executemany(SQL, results)
    conn.commit()


if __name__ == '__main__':
    while 1:
        start = datetime.utcnow()
        main()
        end = datetime.utcnow()
        logging.info("execute: {} - {}".format(start, end))
        duration = end - start
        if duration < timedelta(hours=0.5):
            logging.info("sleep for a while")
            time.sleep(3600)
