import logging
import time
from datetime import datetime

from flask import render_template, request, Blueprint, current_app, session

from db import User, UserStatus

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
    user = User.select(lambda x: x.u_id == u_id and x.status == UserStatus.normal).first()
    if user:
        user.last_login_time = datetime.utcnow()
        logging.info("user u_id: {}".format(user.u_id))
        request.user = user
    else:
        logging.info("user not login")


@page_bp.route('/', methods=['GET'])
def index():
    """根据用户是否登录判断返回页面"""
    # if not hasattr(request, 'user') or not request.user:
    #     return render_template('welcome.html', timestamp=SecretTimestamp(), page='login', msg=None)

    return render_template('index.html')
