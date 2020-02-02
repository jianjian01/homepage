import logging
import time
from datetime import datetime

from flask import render_template, Blueprint

from util.tool import check_user

page_bp = Blueprint('page', __name__, template_folder='templates')

page_bp.before_request(check_user)


@page_bp.route('/', methods=['GET'])
def index():
    """根据用户是否登录判断返回页面"""
    # if not hasattr(request, 'user') or not request.user:
    #     return render_template('welcome.html', timestamp=SecretTimestamp(), page='login', msg=None)

    return render_template('index.html')
