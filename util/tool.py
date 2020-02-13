import logging
import random
import string
from collections import defaultdict
from datetime import datetime
from functools import wraps, lru_cache

from flask import current_app, session, request, redirect, url_for
from pony.orm import commit, db_session

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


def log_request(response):
    """使用 gunicron 时， 自带的 logger 不能使用"""
    logging.info('{} {} {} {}'.format(
        request.headers.get('X-Real-IP', ''),
        request.method, request.path,
        response.status
    ))
    return response


def static_url(path):
    """静态资源使用 单独域名"""
    conf = current_app.config
    domain = conf.get('STATIC_DOMAIN', '')
    scheme = conf.get('PREFERRED_URL_SCHEME', '')
    return '{}://{}/{}'.format(scheme, domain, path)


@lru_cache(maxsize=2020)
def redirect_home():
    """重定向到首页"""
    return redirect(url_for('page.index', _external=True,
                            _scheme=current_app.config['PREFERRED_URL_SCHEME']))


def randstr(length=16):
    return ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(length)])


def guess_locale():
    cl = request.cookies.get('locale', '')
    if not cl:
        cl = request.accept_languages.best_match(current_app.config['I18N_LANGUAGES'])
    if not cl:
        cl = 'en'
    return cl


def batch_insert_website(data, user):
    """批量插入数据
    :type data: dict key -> category, values -> sites
    :type user: User
    """
    with db_session:
        i = 0
        for k, ws in data.items():
            i += 1
            if k:
                c = Category(name=k, user=user, order=10 * i)
            else:
                c = None
            k = 0
            for w in ws:
                k += 1
                UserSite(name=w[0], cate=c, user=user, url=w[1], icon=w[2], order=10 * k)
