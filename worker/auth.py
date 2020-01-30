import logging
import random
import string
from datetime import datetime

import requests
from flask import Blueprint, request, redirect, current_app, session
from pony.orm import commit, db_session

from db import UserSource, User, UserStatus

auth_bp = Blueprint('auth', __name__, template_folder='templates')


def callback_auth(source):
    """检查回调时候 state 是否一致"""

    def wrapper(func):
        def wrapper_inner():
            url_state = request.args.get('state', '')
            cookie_state = request.cookies.get(source, '')
            if len(url_state) != 16 or url_state != cookie_state:
                return redirect('/')
            return func()

        return wrapper_inner

    return wrapper


def save_or_update_user(source, user_id, name, email, content):
    """

    :return:
    """
    if not isinstance(user_id, str):
        user_id = str(user_id)
    if not email:
        email = ''
    user = User.select(lambda x: x.source == source and x.source_id == user_id
                                 and x.status == UserStatus.normal).first()
    if not user:
        user = User(u_id=User.new_uid(), name=name, source=source, source_id=user_id,
                    email=email, source_data=content)
        logging.info("create new user: {}".format(user.u_id))
    else:
        user.name = name
        user.source_data = content
        user.email = email
        user.last_login_time = datetime.utcnow()
        logging.info("user {} login from {}".format(user.u_id, source))
    commit()
    return user.u_id


@auth_bp.route('/')
def login_redirect():
    """

    :return:
    """
    conf = current_app.config
    source = request.args.get('source', '').lower()

    state = ''.join([random.choice(string.digits + string.ascii_lowercase) for _ in range(16)])
    if source == 'github':
        url = 'https://github.com/login/oauth/authorize'
        params = {
            'client_id': conf['GITHUB_CLIENT_ID'],
            'redirect_uri': conf['GITHUB_REDIRECT_URI'],
            'scope': 'read:user',
            'state': state
        }
    else:
        url = "/"
        params = {}
    url = url + "?" + '&'.join(['{}={}'.format(k, v) for k, v in params.items()])
    resp = redirect(url)
    resp.set_cookie(source, state, httponly=True)
    return resp


@auth_bp.route('/callback/github')
@callback_auth('github')
@db_session
def callback_github():
    """处理github回调请求"""
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    conf = current_app.config
    url = "https://github.com/login/oauth/access_token"
    params = {
        'client_id': conf['GITHUB_CLIENT_ID'],
        'client_secret': conf['GITHUB_CLIENT_SECRET'],
        'code': code,
        'state': state
    }
    logging.info("request code {}".format(code))
    resp = requests.post(url=url, params=params, headers={'Accept': 'application/json'})
    logging.info("get response: {}".format(resp.text))
    data = resp.json()
    url = 'https://api.github.com/user'
    token = data.get('access_token', '')
    headers = {
        'Authorization': 'token {}'.format(token),
        'Accept': 'application/json'
    }
    logging.info("request token: {}".format(token))
    resp = requests.get(url=url, headers=headers)
    logging.info("get response: {}".format(resp.text))
    data = resp.json()
    u_id = save_or_update_user(UserSource.github, data.get('id', ''),
                               data.get('name', ''), data.get('email', ''), resp.text)
    session[conf['SESSION_USER']] = u_id
    session.permanent = True
    return redirect('/')
