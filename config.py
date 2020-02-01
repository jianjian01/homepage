import logging
import os


class Base:
    """公共配置"""
    REDIS_VERIFY_EMAIL_CHANNEL = "VERIFY_EMAIL"
    SESSION_USER = '_u'
    SESSION_SOURCE = '_o'
    SESSION_CREATE_TIME = '_t'

    AUTH_SITES = ['weibo', 'github']


class Dev(Base):
    """开发环境"""
    DEBUG = True
    SECRET_KEY = 'testing'  # os.urandom(16)

    PONY = {
        'provider': 'mysql',
        'host': '47.96.177.79',
        'port': 29898,
        'user': 'root',
        'passwd': '8W5Qqv9IfgdvHk',
        'db': 'chidianxin',
    }
    REDIS_URL = 'redis://47.96.177.79:29899/0'
    RANDOM_KEY = os.urandom(16)

    SMTP_HOST = 'smtpdm.aliyun.com'
    SMTP_PORT = 465
    SMTP_EMAIL = 'verify@chidian.xin'
    SMTP_PASSWORD = 'G3iu3hrbwmDz1vcuaHHK'

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

    SESSION_COOKIE_DOMAIN = 'chidian.xin'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_SAMESITE = "Lax"

    PONY = {
        'provider': 'mysql',
        'host': 'mysql_8',
        'port': 3306,
        'user': 'root',
        'passwd': '8W5Qqv9IfgdvHk',
        'db': 'chidianxin',
    }
    REDIS_URL = 'redis://@redis_5:6379/1'

    SMTP_HOST = 'smtpdm.aliyun.com'
    SMTP_PORT = 465
    SMTP_EMAIL = 'verify@chidian.xin'
    SMTP_PASSWORD = 'G3iu3hrbwmDz1vcuaHHK'

    GITHUB_CLIENT_ID = '655c0721a03d26aac38c'
    GITHUB_CLIENT_SECRET = 'a31f81f1ca84b7a9ccc12e4ae3d5ed69338f8128'
    GITHUB_REDIRECT_URI = 'https://chidian.xin/auth/callback/github'
    WEIBO_APP_KEY = '1108861131'
    WEIBO_APP_SECRET = 'b82a3cc00f20ab137e3d572000ad0f08'
    WEIBO_REDIRECT_URI = 'https://chidian.xin/auth/callback/weibo'
    WEIBO_CANCEL_URI = 'https://chidian.xin/auth/callback/weibo/cancel'


Config = None

if os.getenv("ENV", '').lower() == 'production':
    Config = Prod
else:
    Config = Dev


def set_log():
    fmt = "[%(asctime)-15s %(levelname)s %(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO)
    logging.info("running")


set_log()

__all__ = ['Config']
