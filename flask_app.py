from flask import Flask
from flask_redis import FlaskRedis
from flask_wtf import CSRFProtect
from pony.flask import Pony

from config import Config
from db import db as mysql

# flask
flask_app = Flask(__name__)
flask_app.config.from_object(Config)
CSRFProtect(flask_app)

# mysql
mysql.bind(**flask_app.config['PONY'])
mysql.generate_mapping()
pony = Pony(flask_app)

# redis
redis = FlaskRedis(flask_app)

__all__ = ['flask_app', 'pony', 'redis']
