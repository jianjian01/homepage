import asyncio
import logging
import time
from datetime import datetime, timedelta
from time import mktime

import aiohttp
import aiomysql
import feedparser
import pymysql

from config import Config

SQL = "INSERT INTO page (`rss`, `page_id`, `title`, `link`, `publish_date`) " \
      " values (%s, %s, %s, %s, %s)" \
      " ON DUPLICATE KEY UPDATE title=VALUES(title), link=VALUES(link)"


def parser(rss_id, text):
    """解析内容"""
    date_default = datetime.utcnow()
    feed = feedparser.parse(text)
    data = []
    for item in feed.entries:
        struct_time = item.get('published_parsed', None)
        item_id = item.get('id', '')
        item_link = item.get('link', '')
        item_title = item.get('title', '')
        # item_ID 是 主键，不能缺失，如果找不到，就用其他的代替
        if not item_id:
            item_id = item_link
        if not item_id:
            item_id = item_title
        if not item_id:
            continue
        if not struct_time:
            struct_time = item.get('updated_parsed', None)
        pub_date = date_default
        if struct_time:
            try:
                pub_date = datetime.fromtimestamp(mktime(struct_time))
            except Exception:
                print(item)
        data.append([
            rss_id,
            item_id,
            item_title,
            item_link,
            pub_date
        ])

    return data


async def fetch(rss, semaphore, pool):
    rss_id, rss_url = rss
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            try:
                logging.info('start: {}'.format(rss_url))
                async with session.get(rss_url, timeout=20) as response:
                    content = await response.text()
            except Exception as _:
                logging.warning('timeout: {}'.format(rss_url))
                return rss_url, []
            data = parser(rss_id, content)
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    count = await cur.executemany(SQL, data)
                    logging.info("{} insert {} row".format(rss_url, count))
                await conn.commit()
    return rss_url, data


async def run(loop, rss_list, conf):
    """"""
    semaphore = asyncio.Semaphore(conf.RSS_REQUEST_NUM)
    pool = await aiomysql.create_pool(**conf.PONY, loop=loop)
    tasks = []
    for rss in rss_list:
        tasks.append(fetch(rss, semaphore, pool))
    done, pending = await asyncio.wait(tasks)
    for res in done:
        print(res.result())
    for res in pending:
        print(res)

    pool.close()
    await pool.wait_closed()


def main():
    """
    获取 rss 链接
    :return:
    """
    conf = Config()
    conf.PONY.pop('provider', '')
    conn = pymysql.connect(**conf.PONY)
    logging.info("query database")
    with conn.cursor() as cursor:
        cursor.execute("select id, link from rss order by rand()")
        result = cursor.fetchall()
    conn.close()
    logging.info("rss {}".format(len(result)))

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run(loop, result, conf))
    loop.close()


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
