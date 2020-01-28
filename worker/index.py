import time

from flask import render_template, request

from flask_app import flask_app as app
from util.check import SecretTimestamp

from task.mail import send_email_verify_url


@app.route('/', methods=['GET'])
def index():
    """根据用户是否登录判断返回页面"""
    if not hasattr(request, 'user') or not request.user:
        return render_template('welcome.html', timestamp=SecretTimestamp(), page='login')

    return render_template('index.html')
