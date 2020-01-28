import json
import logging
import random
import string

from flask import request, render_template, current_app, jsonify, session

from db import User, UserStatus
from flask_app import flask_app as app, redis
from util.check import register_check, bcrypt_hash, SecretTimestamp, login_check, bcrypt_check


@app.route('/login', methods=['GET'])
def user_login_get():
    """用户登录"""
    return render_template('welcome.html', timestamp=SecretTimestamp(), page='login')


@app.route('/login', methods=['POST'])
def user_login():
    """用户登录"""
    form = request.form
    email = form.get('email')
    password = form.get('password')
    timestamp = form.get('timestamp')
    timestamp_secret = form.get('timestamp_secret')
    res = login_check(email, password, timestamp, timestamp_secret)
    if res:
        return res
    user = User.select(lambda x: x.email == email and x.status in (UserStatus.normal,
                                                                   UserStatus.register, UserStatus.anomaly))
    if not user:
        return jsonify({'status': -1, "message": "用户名或者密码错误"})
    user = user.first()
    if not bcrypt_check(email, password, user.password):
        return jsonify({'status': -1, "message": "用户名或者密码错误"})

    if user.status == UserStatus.register:
        return jsonify({'status': -1, "message": "账户未激活"})
    if user.status == UserStatus.anomaly:
        return jsonify({'status': -1, "message": "账户异常"})
    if user.status == UserStatus.normal:
        resp = jsonify({'status': 1, "message": "登录成功"})
        session.permanent = True
        session['_u'] = user.u_id
        session['_e'] = user.email
        return resp


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
    user = User(name=name, email=email, u_id=User.new_uid(),
                password=bcrypt_hash(email, password))
    v_code = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(32)])
    logging.info("email: {} u_id:{} v_code: {}".format(user.email, user.u_id, v_code))
    res = redis.setex('user:verify:{}'.format(user.u_id), 24 * 60 * 60, v_code)
    logging.info("send v_code to redis success, {}".format(res))
    v_url = "https://chidian.xin/verify?id={}&code={}".format(user.u_id, v_code)
    res = redis.xadd(current_app.config['REDIS_VERIFY_EMAIL_CHANNEL'], {
        'user_id': user.u_id,
        'name': name,
        'email': email,
        'url': v_url,
        'code': v_code
    })
    logging.info("publish send email job success, {}".format(res))
    return jsonify({'status': 1, "message": "注册成功，请查收验证邮件。"})
