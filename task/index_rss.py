import asyncio
import logging
from collections import namedtuple
from datetime import datetime
from itertools import chain
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
        if struct_time:
            published = datetime.fromtimestamp(mktime(struct_time))
        else:
            published = date_default
        data.append([
            rss_id,
            item.id,
            item.title,
            item.link,
            published,
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
        cursor.execute("select id, link from rss")
        result = cursor.fetchall()
    conn.close()
    logging.info("rss {}".format(len(result)))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, result, conf))
    loop.close()


if __name__ == '__main__':
    main()
