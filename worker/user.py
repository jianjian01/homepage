import json
import logging
import random
import string

from flask import request, render_template, current_app, jsonify

from db import User
from flask_app import flask_app as app, redis
from task.mail import send_email_verify_url
from util.check import register_check, bcrypt_hash, SecretTimestamp


@app.route('/login', methods=['GET'])
def user_login_get():
    """用户登录"""
    return render_template('welcome.html', timestamp=SecretTimestamp(), page='login')


@app.route('/login', methods=['POST'])
def user_login():
    """用户登录"""
    return jsonify({})


@app.route('/register', methods=['GET'])
def user_register_get():
    """注册"""
    return render_template('welcome.html', timestamp=SecretTimestamp(), page='register')


@app.route('/register', methods=['POST'])
def user_register():
    """注册"""
    form = request.form
    name = form.get('name')
    email = form.get('email')
    password = form.get('password')
    confirm = form.get('confirm')
    timestamp = form.get('timestamp')
    timestamp_secret = form.get('timestamp_secret')
    # 检查格式
    res = register_check(name, email, password, confirm, timestamp, timestamp_secret)
    if res:
        return res
    #
    user = User(name=name, email=email, u_id=User.new_uid(),
                password=bcrypt_hash(email, password))
    v_code = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(32)])
    logging.info("email: {} u_id:{} v_code: {}".format(user.email, user.u_id, v_code))
    res = redis.setex('user:verify:{}'.format(user.u_id), 24 * 60 * 60, v_code)
    logging.info("send v_code to redis success, {}".format(res))
    v_url = "https://chidian.xin/verify?id={}&code={}".format(user.u_id, v_code)
    res = redis.publish(current_app.config['REDIS_VERIFY_EMAIL_CHANNEL'], json.dumps({
        'name': name,
        'email': email,
        'url': v_url,
        'code': v_code
    }))
    logging.info("publish send email job success, {}".format(res))
    return jsonify({'status': 1, "message": "注册成功，请查收验证邮件。"})
