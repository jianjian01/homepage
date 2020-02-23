# 下载 icon
import os
from urllib.parse import urlparse

import pymysql
import requests
from qiniu import Auth, put_file
from redis import Redis

from config import Config
from util.tool import parse_icon_html, download_icon

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


def fetch(url):
    """
    获取 icon url
    :param url:
    :return:
    """
    headers['Host'] = urlparse(url).netloc
    session = requests.Session()
    resp = session.get(url, headers=headers)
    new_url = resp.url
    us = urlparse(new_url)
    icons = parse_icon_html(resp.content, new_url)
    if not icons:
        icons = ['{}://{}/{}'.format(us.scheme, us.netloc, "favicon.ico")]
    for icon_url in icons:
        headers['Host'] = us.netloc
        resp = session.get(icon_url, headers=headers, stream=True)
        icon = download_icon(resp)
        if icon:
            return icon


def main():
    """

    :return:
    """
    mysql_config = Config.PONY
    mysql_config.pop('provider', '')
    redis = Redis.from_url(Config.REDIS_URL)
    mysql = pymysql.Connect(**mysql_config)
    q = Auth(Config.QINIU_ACCESS_KEY, Config.QINIU_ACCESS_SECRET)

    ps = redis.pubsub()
    ps.subscribe(Config.REDIS_DOWNLOAD_ICON_CHANNEL)
    for item in ps.listen():
        if item['type'] != 'message':
            continue
        data = item.get('data', '')
        print(data)
        if not data:
            continue
        with mysql.cursor() as cursor:
            cursor.execute("select id, url, icon from usersite where id=%s", [data])
            user_site = cursor.fetchone()
            url = user_site[1]
            icon = fetch(url)
            us = urlparse(url)
            if not icon:
                continue
            cursor.execute("update  usersite  set icon = %s where id=%s", [icon, data])
            cursor.execute("REPLACE INTO `site` (`host`, `icon`) VALUES (%s, %s)", [us.netloc, icon])
            mysql.commit()
        key = 'site/{}.png'.format(icon)
        token = q.upload_token(Config.QINIU_BUCKET, key, 60)
        ret, info = put_file(token, key, os.path.join(Config.ICON_DIR, '{}.png'.format(icon)))
        print(info)


if __name__ == '__main__':
    main()
