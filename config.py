import os


class Dev:
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
    REDIS_URL = 'redis://@47.96.177.79:29899/0'
    CELERY_BROKER_URL = 'redis://@47.96.177.79:29899/1'
    CELERY_RESULT_BACKEND = 'redis://@47.96.177.79:29899/1'
    SMTP_HOST = 'smtpdm.aliyun.com'
    SMTP_PORT = 465
    SMTP_EMAIL = 'verify@chidian.xin'
    SMTP_PASSWORD = 'G3iu3hrbwmDz1vcuaHHK'


class Prod:
    """正式环境"""
    DEBUG = False

    SESSION_COOKIE_DOMAIN = 'chidian.xin'
    SESSION_COOKIE_HTTPONLY = True
    PONY = {
        'provider': 'mysql',
        'host': 'mysql_8',
        'port': 3306,
        'user': 'root',
        'passwd': '8W5Qqv9IfgdvHk',
        'db': 'chidianxin',
    }
    REDIS_URL = 'redis://@redis_5:6379/1'
    CELERY_BROKER_URL = 'redis://@redis_5:6379/1'
    CELERY_RESULT_BACKEND = 'redis://@redis_5:6379/1'
    SMTP_HOST = 'smtpdm.aliyun.com'
    SMTP_PORT = 465
    SMTP_EMAIL = 'verify@chidian.xin'
    SMTP_PASSWORD = 'G3iu3hrbwmDz1vcuaHHK'


Config = None

if os.getenv("ENV", '').lower() == 'production':
    Config = Prod
else:
    Config = Dev

__all__ = ['Config']
