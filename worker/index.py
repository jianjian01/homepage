import logging
import time
from datetime import datetime

from flask import render_template, request, Blueprint, current_app, session

from db import User, UserStatus
from flask_app import redis
from util.tool import random_str

page_bp = Blueprint('page', __name__, template_folder='templates')

page_bp.before_request(lambda: check_user())


def check_user():
    """
    检查用户状态
    :return:
    """
    conf = current_app.config
    u_id = session.get(conf['SESSION_USER'])
    if not u_id or not isinstance(u_id, int):
        return
    su_id = str(u_id)
    ran_str = session.get(su_id)
    rds_str = redis.get(su_id)
    if not rds_str or rds_str.decode() != ran_str:
        return
    user = User.select(lambda x: x.u_id == u_id and x.status == UserStatus.normal).first()
    if user:
        user.last_login_time = datetime.utcnow()
        logging.info("user u_id: {}".format(user.u_id))
        redis.setex(str(u_id), 24 * 60 * 60 * 7, ran_str)
        request.user = user
    else:
        logging.info("user not login")


@page_bp.route('/', methods=['GET'])
def index():
    """根据用户是否登录判断返回页面"""
    # if not hasattr(request, 'user') or not request.user:
    #     return render_template('welcome.html', timestamp=SecretTimestamp(), page='login', msg=None)

    return render_template('index.html')
