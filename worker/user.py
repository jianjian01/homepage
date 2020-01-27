from flask import request, render_template, url_for, redirect, flash, jsonify

from db import User
from flask_app import flask_app as app
from task.mail import send_email_verify_url
from util.check import register_check, bcrypt_hash


@app.route('/login', methods=['GET'])
def user_login_get():
    """用户登录"""
    return redirect('/')


@app.route('/login', methods=['POST'])
def user_login():
    """用户登录"""
    return jsonify({})


@app.route('/register', methods=['GET'])
def user_register_get():
    """注册"""
    return redirect('/')


@app.route('/register', methods=['POST'])
def user_register():
    """注册"""
    form = request.form
    name = form.get('name')
    email = form.get('email')
    password = form.get('password')
    confirm = form.get('confirm')
    # 检查格式
    res = register_check(name, email, password, confirm)
    if res:
        return res
    user = User(name=name, email=email, u_id=User.new_uid(),
                password=bcrypt_hash(email, password))
    send_email_verify_url.apply_async(
        args=(name, email, "https://chidian.xin/verify?id=abcd&code=asdfhajksdfhakjsdfhaljkdfhal"))
    return jsonify({'status': 1, "message": "注册成功，请查收验证邮件。"})
