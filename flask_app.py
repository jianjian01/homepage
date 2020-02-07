from flask import Flask, request, current_app
from flask_babel import Babel
from flask_redis import FlaskRedis
from flask_wtf import CSRFProtect
from pony.flask import Pony

from config import Config
from db import db as mysql

# flask
flask_app = Flask(__name__)
flask_app.config.from_object(Config)
flask_app.jinja_env.add_extension('jinja2.ext.i18n')

CSRFProtect(flask_app)

# mysql
mysql.bind(**flask_app.config['PONY'])
mysql.generate_mapping()
pony = Pony(flask_app)

# redis
redis = FlaskRedis(flask_app)

babel = Babel(flask_app)


@babel.localeselector
def get_locale():
    locale = request.cookies.get('locale', '')
    if locale:
        return locale
    return request.accept_languages.best_match(current_app.config['I18N_LANGUAGES'])


@babel.timezoneselector
def get_timezone():
    """设置 时区"""
    # todo


__all__ = ['flask_app', 'pony', 'redis', 'babel']
