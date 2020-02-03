import logging
import random
import string
from collections import defaultdict
from datetime import datetime
from functools import wraps

from flask import current_app, session, request, redirect
from pony.orm import commit

from db import User, UserStatus, UserSite, Category, UserSiteStatus, Site
from flask_app import redis


def random_str(length):
    return ''.join([random.choice(string.digits + string.ascii_lowercase) for _ in range(length)])


def check_user():
    """
    检查用户状态
    :return:
    """
    conf = current_app.config
    u_id = session.get(conf['SESSION_USER'])
    ct = session.get(conf['SESSION_CREATE_TIME'])
    if not u_id or not isinstance(u_id, int):
        return
    su_id = str(u_id)
    key = "{}:{}".format(su_id, ct)
    ran_str = session.get(su_id)
    rds_str = redis.get(key)
    if not rds_str or rds_str.decode() != ran_str:
        return
    user = User.select(lambda x: x.u_id == u_id and x.status == UserStatus.normal).first()
    if user:
        user.last_login_time = datetime.utcnow()
        logging.info("user u_id: {}".format(user.u_id))
        redis.setex(key, 24 * 60 * 60 * 7, ran_str)
        request.user = user
    else:
        logging.info("user not login")
        request.user = None


def login_require(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(request, 'user') or not request.user:
            return redirect('/')
        return func(*args, **kwargs)

    return wrapper


def select_website():
    """查询当前用户的网址"""
    sites = UserSite.select(lambda x: x.user == request.user and x.status == UserSiteStatus.normal)[:]
    categories = Category.select(lambda c: c.user == request.user and not c.delete).order_by(Category.order)[:]
    ss = defaultdict(list)
    for s in sites:
        key = s.cate.id if s.cate else ""
        ss[key].append(s)
    categories = list(categories)
    categories.insert(0, {"id": '', 'name': '', 'order': 0})
    return ss, categories


def query_icon(host):
    """查询host 对应的 icon"""
    site = Site.select(lambda x: x.host == host).first()
    if not site:
        _ = Site(host=host, icon='')
        return ''
    return site.icon
