import logging
import os
from logging.handlers import TimedRotatingFileHandler

from pony.orm import set_sql_debug


class Base:
    """公共配置"""
    REDIS_VERIFY_EMAIL_CHANNEL = "VERIFY_EMAIL"
    SESSION_USER = '_u'
    SESSION_SOURCE = '_o'
    SESSION_CREATE_TIME = '_t'
    RSS_REQUEST_NUM = 50  # 定时任务 index rss 异步执行数量
    I18N_LANGUAGES = ['zh', 'ja', 'en']
    BABEL_TRANSLATION_DIRECTORIES = './translations'

    AUTH_SITES = ['weibo', 'github']


class Dev(Base):
    """开发环境"""
    DEBUG = True
    SECRET_KEY = 'testing'  # os.urandom(16)
    STATIC_DOMAIN = "127.0.0.1:5000/static"
    ICON_DIR = '/Users/jianjian/github/jianjian01/dian-xin/static/site/'

    PONY = {
        'provider': 'mysql',
        'host': '47.96.177.79',
        'port': 29898,
        'user': 'root',
        'password': '8W5Qqv9IfgdvHk',
        'db': 'chidianxin',
        'autocommit': 'True',
    }
    REDIS_URL = 'redis://47.96.177.79:29899/0'
    RANDOM_KEY = os.urandom(16)

    GITHUB_CLIENT_ID = '655c0721a03d26aac38c'
    GITHUB_CLIENT_SECRET = 'a31f81f1ca84b7a9ccc12e4ae3d5ed69338f8128'
    GITHUB_REDIRECT_URI = 'http://127.0.0.1:5000/auth/callback/github'
    WEIBO_APP_KEY = '1108861131'
    WEIBO_APP_SECRET = 'b82a3cc00f20ab137e3d572000ad0f08'
    WEIBO_REDIRECT_URI = 'http://127.0.0.1:5000/auth/callback/weibo'
    WEIBO_CANCEL_URI = 'http://127.0.0.1:5000/auth/callback/weibo/cancel'


class Prod(Base):
    """正式环境"""
    DEBUG = False

    SESSION_COOKIE_DOMAIN = 'myweb100.com'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SECRET_KEY = 'wSt0QSG9fnfPGmiB'
    PREFERRED_URL_SCHEME = "https"
    SERVER_NAME = 'myweb100.com'
    STATIC_DOMAIN = "static.myweb100.com"
    ICON_DIR = '/app/static/site/'

    PONY = {
        'provider': 'mysql',
        'host': 'mysql',
        'port': 3306,
        'user': 'myweb',
        'password': 'T3KfkTjGmXE1ar5p',
        'db': 'myweb',
        'autocommit': 'True',
    }
    REDIS_URL = 'redis://@redis:6379/1'

    GITHUB_CLIENT_ID = '655c0721a03d26aac38c'
    GITHUB_CLIENT_SECRET = 'a31f81f1ca84b7a9ccc12e4ae3d5ed69338f8128'
    GITHUB_REDIRECT_URI = 'https://myweb100.com/auth/callback/github'
    WEIBO_APP_KEY = '1108861131'
    WEIBO_APP_SECRET = 'b82a3cc00f20ab137e3d572000ad0f08'
    WEIBO_REDIRECT_URI = 'https://myweb100.com/auth/callback/weibo'
    WEIBO_CANCEL_URI = 'https://myweb100.com/auth/callback/weibo/cancel'
    GOOGLE_CLIENT_ID = '925382553833-t8ieg4gc6df1sr6kum3fldurrvi6rtke.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = 'DUMbH8oL6dGSJoNk9NJq9bja'
    GOOGLE_REDIRECT_URI = 'https://myweb100.com/auth/callback/google'



Config = None

mode = os.getenv("mode", '').lower()

if mode == 'production':
    Config = Prod
else:
    set_sql_debug()
    Config = Dev


def set_log():
    fmt = "[%(asctime)-15s %(levelname)s %(filename)s:%(lineno)d] %(message)s"
    if mode == 'production':
        os.makedirs('logs', exist_ok=True)
        filename = './logs/.log'
        handler = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=180,
                                           encoding=None, delay=False, utc=True)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger = logging.getLogger()
        # while running gunicron, flask.logger not work
        gunicorn_logger = logging.getLogger('gunicorn.error')
        gunicorn_logger.addHandler(handler)
        logger.handlers = gunicorn_logger.handlers
        logger.setLevel(gunicorn_logger.level)
        logging.handlers = gunicorn_logger.handlers
        logging.info("running gunicorn_logger")
    else:
        logging.basicConfig(format=fmt, level=logging.INFO)
        logging.info("running dev")


set_log()

__all__ = ['Config']
