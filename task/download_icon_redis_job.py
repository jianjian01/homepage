# 下载 icon
# 订阅 redis 频道, 收到 usersite id 后抓取对应网站的 icon, 保存到本地 ICON_DIR
import os
import time
from urllib.parse import urlparse

import pymysql
import requests
import urllib3
from redis import Redis

from config import Config
from util.tool import parse_icon_html, randstr

urllib3.disable_warnings()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15",
    "Accept-Language": "zh-cn",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

GOOGLE_FAVICON = 'https://www.google.com/s2/favicons?domain={}&sz=64'

# 常见图片格式的魔数
MAGIC = (
    b'\x89PNG',      # png
    b'\xff\xd8\xff',  # jpeg
    b'GIF8',         # gif
    b'\x00\x00\x01\x00',  # ico
    b'RIFF',         # webp (RIFF....WEBP)
    b'<?xml',        # svg
    b'<svg',         # svg
)


def is_image(content):
    """校验下载到的内容确实是图片"""
    if not content or len(content) < 50:
        return False
    return any(content.startswith(m) for m in MAGIC)


def save_icon(content):
    """保存 icon 到本地, 返回文件名(不带扩展名), 失败返回 None"""
    if not os.path.exists(Config.ICON_DIR):
        os.makedirs(Config.ICON_DIR)
    while 1:
        file_name = randstr(16)
        path = os.path.join(Config.ICON_DIR, '{}.png'.format(file_name))
        if not os.path.exists(path):
            break
    with open(path, mode='wb') as f:
        f.write(content)
    return file_name


def download(url, strict_status=True):
    """下载并校验一个 icon url, 成功返回文件名, 失败返回 None"""
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
    except Exception:
        return None
    if strict_status and resp.status_code != 200:
        return None
    if not is_image(resp.content):
        return None
    return save_icon(resp.content)


def fetch(url):
    """
    获取 url 对应的 icon, 依次尝试:
    1. 抓取网页 HTML, 解析 <link rel="icon">
    2. 直接请求 /favicon.ico
    3. 谷歌 favicon 服务兜底
    成功返回文件名, 失败返回 None
    """
    us = urlparse(url)
    base = '{}://{}'.format(us.scheme or 'https', us.netloc)

    icons = []
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        if resp.status_code == 200:
            icons = parse_icon_html(resp.content, resp.url) or []
    except Exception:
        pass

    icons.append('{}/favicon.ico'.format(base))
    for icon_url in icons:
        name = download(icon_url)
        if name:
            return name

    # 谷歌服务兜底: 未知域名谷歌返回 404 + 默认地球图标, 只要内容是图片就接受, 保证不为空
    # 域名带端口时谷歌会返回错误页, 用 hostname 去掉端口
    return download(GOOGLE_FAVICON.format(us.hostname or us.netloc), strict_status=False)


def handle(mysql, usersite_id):
    with mysql.cursor() as cursor:
        cursor.execute("select id, url, icon from usersite where id=%s", [usersite_id])
        user_site = cursor.fetchone()
        if not user_site:
            print('usersite {} not found'.format(usersite_id))
            return
        if user_site[2]:
            return
        icon = fetch(user_site[1])
        if not icon:
            print('usersite {} icon fetch failed: {}'.format(usersite_id, user_site[1]))
            return
        host = urlparse(user_site[1]).netloc
        cursor.execute("update usersite set icon = %s where id=%s", [icon, usersite_id])
        cursor.execute("REPLACE INTO `site` (`host`, `icon`) VALUES (%s, %s)", [host, icon])
    mysql.commit()
    print('usersite {} icon -> {}'.format(usersite_id, icon))


def main():
    mysql_config = dict(Config.PONY)
    mysql_config.pop('provider', '')
    redis = Redis.from_url(Config.REDIS_URL)
    mysql = pymysql.Connect(**mysql_config)

    ps = redis.pubsub()
    ps.subscribe(Config.REDIS_DOWNLOAD_ICON_CHANNEL)
    print('listen channel: {}'.format(Config.REDIS_DOWNLOAD_ICON_CHANNEL))
    for item in ps.listen():
        if item['type'] != 'message':
            continue
        data = item.get('data', '')
        if not data:
            continue
        try:
            mysql.ping(reconnect=True)
            handle(mysql, int(data))
        except Exception as e:
            print('handle {} error: {}'.format(data, e))


if __name__ == '__main__':
    while 1:
        try:
            main()
        except Exception as e:
            print('main error: {}, retry in 5s'.format(e))
            time.sleep(5)
