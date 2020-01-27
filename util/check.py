import base64
import hashlib
import string
from email.utils import parseaddr

import bcrypt
from flask import jsonify

from db import User, UserStatus


def register_check(name, email, password, confirm):
    """注册检查"""
    if not 4 <= len(name) <= 32:
        return jsonify({'status': -1, "message": "用户名长度需要为 4 到 32 之间"})
    es = email.split("@", 1)
    if len(es) != 2 or not es[1] or [t for t in es[1].split('.') if not t]:
        return jsonify({'status': -1, "message": "邮件地址格式不正确"})
    cp = check_password(password)
    if not cp[0]:
        return jsonify(cp[1])
    if password != confirm:
        return jsonify({'status': -1, "message": "密码不一致"})
    # 检查有没有注册过
    if User.email_status(email) != UserStatus.not_exist:
        return jsonify({'status': -1, "message": "邮箱已经注册"})

    return None


def check_password(pwd):
    """检查密码格式"""
    num, letter, other = False, False, False
    if not 8 < len(pwd) < 32:
        return False, {'status': -1, "message": "密码长度需要在 8 到 32 位之间"}
    for c in pwd:
        if c in string.digits:
            num = True
            continue
        if c in string.ascii_letters:
            letter = True
            continue
        other = True
    if not num or not letter or not other:
        return False, {'status': -1, "message": "密码需要同时包含 数字、字母、和特殊字符"}
    return True, ''


def bcrypt_hash(email, password):
    """
    使用 bcrypt 算法加密
    :param name:
    :param password:
    :return:
    """
    pwd = base64.b64encode(hashlib.sha256((email + password).encode()).digest())
    return bcrypt.hashpw(pwd, bcrypt.gensalt(14)).decode()


def bcrypt_check(email, password, hashed):
    """
    :param name:
    :param password:
    :return:
    """
    pwd = base64.b64encode(hashlib.sha256((email + password).encode()).digest())
    return bcrypt.checkpw(pwd, hashed.encode())
