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

    ZH_INIT_SITES = {
        '': [
            ['人民网', 'http://www.people.com.cn/', 'tvvb8l0fjen4fw17'],
            ['腾 讯', 'https://www.qq.com', 'cwj3k8eoj19m4cje'],
            ['知 乎', 'https://www.zhihu.com/', '3l85yxb646fyo8hm'],
            ['微 博', 'https://weibo.com', 'ggxjpao0l2i3cu4x'],
            ['豆 瓣', 'https://www.douban.com', '2cws801nb8hmc8ck'],
            ['搜 狗', 'https://www.sogou.com', 'k1nm02q6nleih2eb'],
            ['淘 宝', 'https://www.taobao.com/', '21gnefna5199gpij'],
            ['京 东', 'https://www.jd.com/', 'j7hagpmu75tl1623'],
            ['腾讯视频', 'https://v.qq.com', '6e0p469y48w82a8z'],
            ['优 酷', 'https://youku.com/', 'czvgza9l10gyh7gz'],
            ['爱奇艺', 'https://iqiyi.com', 'bfm3bwtkyla8ym3y'],
        ],
        '购物旅游': [
            ['蘑菇街', 'https://www.mogu.com/', 'xns64gmejpsqchqk'],
            ['唯品会', 'https://www.vip.com/', 'hwmssa4iwfry9jcz'],
            ['天猫商城', 'https://www.tmall.com/', 'hoqja02he360o76m'],
            ['苏宁易购', 'https://www.suning.com/', 'ucwl8rbmdla74dm1'],
            ['什么值得买', 'https://www.smzdm.com/', 'rla9rji89uibtyum'],
            ['苹果官网', 'https://www.apple.com.cn/', '9hiuu8rrqounnmfu'],
            ['途牛旅游', 'https://www.tuniu.com', 'cnoqpwbg1y7cqmzp'],
            ['携程旅行', 'https://www.ctrip.com/', 'dxdrbj9nkkq1hxcs'],
            ['飞猪旅行', 'https://www.fliggy.com', '4f3q0prbswuj3915'],
            ['Booking 缤客', 'https://www.booking.com/', '5eafo3tusqacf8hn'],
            ['安彼迎', 'https://www.airbnb.cn', 'xul8uyzlbwi23csl'],
            ['马蜂窝', 'http://www.mafengwo.cn/', 'knt07gulque1cvkd'],
        ],
        '娱乐': [
            ['CCTV', 'https://www.cctv.com', 'h7qcvs6z48lqqth8'],
            ['芒果 TV', 'https://www.mgtv.com', 'aq20edj6fmtet048'],
            ['哔哩哔哩', 'https://www.bilibili.com', '6h0fv90ha8oxxdxg'],
            ['斗 鱼', 'https://www.douyu.com/', 'fo0zw326vs450pr2'],
            ['一直播', 'https://www.yizhibo.com/', 'pxwqspjx39sirh4e'],
        ],
        '阅读学习': [
            ['豆瓣阅读', 'https://read.douban.com/', '8v6eh9e5jhzmu7np'],
            ['南方周末', 'http://www.infzm.com/', '0bsmwwszueoh4th3'],
            ['好大学在线', 'https://www.cnmooc.org/', 'qpji0y72w4npgds8'],
            ['学堂在线', 'https://next.xuetangx.com/', '20pitg7ixwr1jxa2'],
            ['网易公开课', 'https://open.163.com/', 'ozgh856tbzl0nrqr'],
            ['优达学城', 'https://cn.udacity.com/', 'l19av1zal2wgkg9r'],
        ],
        '常用工具': [
            ['坚果云', 'https://www.jianguoyun.com/', 'pk4mui6kg1wd8c6k'],
            ['飞书', 'https://www.feishu.cn', 'ytxxu7hanawoz9bt'],
            ['QQ 邮箱', 'https://mail.qq.com/', '19d6z52vlx7kb01i'],
            ['开源中国', 'https://www.oschina.net', '87fze5sr7ylpjtqp'],
            ['GitHub', 'https://github.com', 'xd22bo52y59b4xfe'],
            ['汽车之家', 'https://www.autohome.com.cn/', 'b82lf9d77thteprk'],
        ]
    }

    EN_INIT_SITES = {
        '': [
            ['Google', 'https://www.google.com/', 'u3xxg7fesejpfaia'],
            ['Yahoo', 'https://www.yahoo.com/', 'll1u8yp4thnm21i8'],
            ['AOL', 'https://www.aol.com', 'll1u8yp4thnm21i7'],
            ['Twitter', 'https://twitter.com/', 'y93kbj25n6a0tlew'],
            ['Instagram', 'https://www.instagram.com/', '5vmmzgx57ov97uc9'],
            ['Facebook', 'https://www.facebook.com/', 'l58vi9tu9717hro4'],
            ['Amazon', 'https://www.amazon.com/', '2rtv2h42n638j6es'],
            ['Gmail', 'https://mail.google.com/', 'f99qjei2bs0zq0hm'],
            ['Yahoo Mail', 'https://mail.yahoo.com/', 'r0gaut9u50navci9'],
            ['Outlook', 'https://outlook.live.com/', '9uah8dermz57fuoa'],
            ['Google Docs', 'https://docs.google.com', 'u3xxg7fesejpfaia']
        ],
        'News': [
            ['Weather', 'https://weather.com/', 'g5z6wnzgoq6f2gkq'],
            ['The Economist', 'https://www.economist.com/', '8ekaswsabqgg56fy'],
            ['Forbes', 'https://www.forbes.com/', 'd4f8xr2s0g3qx59r'],
            ['The NYTimes', 'https://www.nytimes.com/', 'g4w1o8o4jdj4i2mj'],
            ['Bloomberg', 'https://www.bloomberg.com', 'zce440glc3i2oxt1'],
            ['Quora', 'https://www.quora.com/', 'zm72kj1829ok4ctd']
        ],
        'Entertainment': [
            ['YouTube', 'https://www.youtube.com', 'w87njg04kk0ippkk'],
            ['Netflix', 'https://www.netflix.com/', 'mekpdam2a6v4ug4f'],
            ['Hulu', 'https://www.hulu.com', 'h13wpnnpwydqhegn'],
            ['Twitch', 'https://www.twitch.tv/', 'ac5svyy8ye9h9zd6'],
            ['Spotify', 'http://spotify.com/', 'owwh91ih8vg22tv6'],
            ['TIKTOK', 'https://www.tiktok.com', 'gsd8y4ewwtj7x8rw']
        ],
        'Shopping': [
            ['eBuy', 'https://www.ebay.com/', '6bl4r97r02dy79vh'],
            ['Tmall', 'https://www.tmall.com/', 'hoqja02he360o76m'],
            ['Walmart', 'https://www.walmart.com/', 'wgp5esqe2z14r4d8'],
            ['Best Buy', 'https://www.bestbuy.com/', 'n77xp5nkw98nfqtv'],
            ['Yelp', 'https://www.yelp.com/', 'zt972jvdp1ahznuo'],
            ['Groupon', 'https://www.groupon.com/', 'i0gamwbufhoou6sg']
        ]

    }


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
    STATIC_DOMAIN = "myweb.chidian.xin"
    ICON_DIR = '/static/site/'

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
