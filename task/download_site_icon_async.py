"""
1. 获取 500 个没有 icon 的 Site
2. 创建异步任务
3. 最大执行数 50， 异步执行，
4. 结果一次插入数据库
"""

import asyncio
import logging
import os
import random
import string
from datetime import datetime
from urllib.parse import urlparse

import aiofiles
import aiohttp
import aiomysql
import bs4
import pymysql

from config import Config
from util.tool import randstr

Config.PONY.pop('provider', '')

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Host": "",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15",
    "Accept-Language": "zh-cn",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}


def host_to_url(host, icon=''):
    """拼接url"""
    urls = [
        ['https', host, icon],
        ['http', host, icon]
    ]
    if host.startswith('www.'):
        urls.append(['https', host[4:], icon])
        urls.append(['http', host[4:], icon])
    else:
        urls.append(['https', 'www.{}'.format(host), icon])
        urls.append(['http', 'www.{}'.format(host), icon])
    return urls


def get_icon(content, response, url, host):
    icons = []
    root = bs4.BeautifulSoup(content, "lxml")
    for l in root.find('head').find_all('link'):
        if l.get('rel') and 'icon' in l.get('rel') and l.get('href'):
            href = l.get('href', '')
            if not href:
                return
            if href.startswith('//'):
                href = '{}:{}'.format(url[0], href)
            elif href.startswith('/'):
                href = '{}://{}{}'.format(url[0], host, href)
            elif href.startswith('http'):
                pass
            else:
                rurl = str(response.url)
                rsurl = urlparse(rurl)
                if rsurl.path:
                    rurl = rurl.split('/')[:-1]
                    rurl.append(href)
                    href = '/'.join(rurl)
                else:
                    href = '{}/{}'.format(rurl, href)
            icons.append(href)
    return icons


async def try_head(host):
    async with aiohttp.ClientSession() as session:
        for ur in host_to_url(host):
            url = '{}://{}/{}'.format(*ur)
            print('{} {}'.format(host, url))
            try:
                headers['Host'] = ur[1]
                async with session.get(url, headers=headers, timeout=20) as response:
                    content = await response.text()
                    icons = get_icon(content, response, url, host)
                if icons:
                    return icons
            except Exception as e:
                print(e)

    return []


async def download(response):
    while 1:
        file_name = randstr(16)
        path = os.path.join(Config.ICON_DIR, '{}.png'.format(file_name))
        if not os.path.exists(path):
            break
    file = await aiofiles.open(path, mode='wb')
    await file.write(await response.read())
    await file.close()
    if os.path.exists(path):
        if os.path.getsize(path) < 500:
            os.remove(path)
        return file_name
    return None


async def try_download(url, host):
    """尝试对 获取到的 icon url，下载 """
    async with aiohttp.ClientSession() as session:
        try:
            headers['Host'] = host
            async with session.get(url, headers=headers, timeout=20) as response:
                if response.status != 200:
                    return None
                return await download(response)
        except Exception as e:
            print(e)


async def try_icon_direct(host):
    async with aiohttp.ClientSession() as session:
        for ur in host_to_url(host, 'favicon.ico'):
            url = '{}://{}/{}'.format(*ur)
            print('{} {}'.format(host, url))
            try:
                headers['Host'] = host
                async with session.get(url, headers=headers, timeout=20) as response:
                    if response.status != 200:
                        return None
                    icon_id = await download(response)
                    if icon_id:
                        return icon_id
            except Exception as e:
                print(e)
    return None


async def fetch(site, semaphore):
    """对于 site 的处理"""
    host = site[1]
    print(host)

    async with semaphore:
        try:
            # 首先尝试进入首页，查找 head link 标签，获得 icon 地址
            icons = await try_head(host)
            icon_id = None
            if icons:
                # 如果找到，就直接尝试下载
                for icon in icons:
                    icon_id = await try_download(icon, host)
                    if icon_id:
                        break
            # 如果没有找到，或者没有下载成功
            if not icon_id:
                icon_id = await try_icon_direct(host)
            print("host: {}, icon id: {}".format(host, icon_id))
            return icon_id, site[0]
        except Exception as e:
            logging.info(e)


def save(conn, data):
    """插入数据库"""
    sql = 'update site set icon=%s where id=%s'
    with conn.cursor() as cursor:
        cursor.executemany(sql, data)
    conn.commit()


async def run(loop, sites, conn):
    semaphore = asyncio.Semaphore(Config.RSS_REQUEST_NUM)
    # pool = await aiomysql.create_pool(**Config.PONY, loop=loop)
    tasks = []
    for s in sites:
        tasks.append(fetch(s, semaphore))
    done, pending = await asyncio.wait(tasks)
    data = []
    for d in done:
        res = d.result()
        if res[0]:
            data.append(res)
    print(data)
    # data = [d.result() for d in done]
    save(conn, data)


def main():
    """
    获取 rss 链接
    :return:
    """
    conn = pymysql.connect(**Config.PONY)
    logging.info("query database")
    sql = "select `id`, `host` from site where icon = '' order by rand() limit %s"
    with conn.cursor() as cursor:
        cursor.execute(sql, [200])
        result = cursor.fetchall()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, result, conn))
    loop.close()
    conn.close()


if __name__ == '__main__':
    start = datetime.utcnow()
    main()
    end = datetime.utcnow()
    print("execute: {} - {}".format(start, end))
