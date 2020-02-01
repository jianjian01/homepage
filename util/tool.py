import logging
import random
import string
from datetime import datetime

from flask import current_app, session, request

from db import User, UserStatus
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
