from celery import Celery
from flask import Flask
from flask_redis import FlaskRedis
from flask_wtf import CSRFProtect
from pony.flask import Pony

from config import Config
from db import db as mysql
from task import mail as _

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


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(**app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = make_celery(flask_app)

__all__ = ['flask_app', 'pony', 'redis', 'celery_app']
