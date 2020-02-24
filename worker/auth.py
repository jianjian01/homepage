import logging
import time
from datetime import datetime
from functools import wraps
import requests
from flask import Blueprint, request, redirect, current_app, session
from pony.orm import commit, db_session

from db import UserSource, User, UserStatus
from flask_app import redis
from util.tool import random_str, redirect_home, guess_locale, batch_insert_website

auth_bp = Blueprint('auth', __name__, template_folder='templates')


def callback_auth(source):
    """检查回调时候 state 是否一致"""

    def wrapper(func):
        @wraps(func)
        def wrapper_inner():
            url_state = request.args.get('state', '')
            cookie_state = request.cookies.get(source, '')
            if len(url_state) != 16 or url_state != cookie_state:
                return redirect('/')
            return func()

        return wrapper_inner

    return wrapper


def save_or_update_user(source, user_id, name, avatar_url, content):
    """

    :return:
    """
    if not isinstance(user_id, str):
        user_id = str(user_id)
    if not avatar_url:
        avatar_url = ''
    conf = current_app.config
    user = User.select(lambda x: x.source == source and x.source_id == user_id
                                 and x.status == UserStatus.normal).first()
    if not user:
        user = User(u_id=User.new_uid(), name=name, source=source, source_id=user_id,
                    avatar_url=avatar_url, source_data=content)
        cl = guess_locale()
        if cl == 'zh':
            batch_insert_website(conf['ZH_INIT_SITES'], user)
        elif cl == 'jp':
            pass
        else:
            batch_insert_website(conf['EN_INIT_SITES'], user)
        logging.info("create new user: {}".format(user.u_id))
    else:
        user.name = name
        user.source_data = content
        user.avatar_url = avatar_url
        user.last_login_time = datetime.utcnow()
        logging.info("user {} login from {}".format(user.u_id, source))
    commit()
    return user.u_id


def set_session(conf, u_id, source):
    ct = int(time.time())
    session[conf['SESSION_USER']] = u_id
    session[conf['SESSION_SOURCE']] = source
    session[conf['SESSION_CREATE_TIME']] = ct
    u_id = str(u_id)
    key = "{}:{}".format(u_id, ct)

    ran_str = random_str(8)
    session[u_id] = ran_str
    redis.setex(key, 24 * 60 * 60 * 7, ran_str)
    session.permanent = True


@auth_bp.route('/')
def login_redirect():
    """

    :return:
    """
    conf = current_app.config
    source = request.args.get('source', '').lower()

    state = random_str(16)
    if source == 'github':
        url = 'https://github.com/login/oauth/authorize'
        params = {
            'client_id': conf['GITHUB_CLIENT_ID'],
            'redirect_uri': conf['GITHUB_REDIRECT_URI'],
            'scope': 'read:user',
            'state': state
        }
    elif source == 'weibo':
        url = 'https://api.weibo.com/oauth2/authorize'
        params = {
            'client_id': conf['WEIBO_APP_KEY'],
            'response_type': 'code',
            'redirect_uri': conf['WEIBO_REDIRECT_URI'],
            'scope': 'email',
            'state': state
        }
    elif source == 'google':
        url = 'https://accounts.google.com/o/oauth2/v2/auth'
        params = {
            'client_id': conf['GOOGLE_CLIENT_ID'],
            'response_type': 'code',
            'redirect_uri': conf['GOOGLE_REDIRECT_URI'],
            'scope': 'openid profile email',
            'nonce': random_str(16),
            'state': state,
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
    logging.info("github request code {}".format(code))
    resp = requests.post(url=url, params=params, headers={'Accept': 'application/json'})
    logging.info("github get response: {}".format(resp.text))
    data = resp.json()
    url = 'https://api.github.com/user'
    token = data.get('access_token', '')
    headers = {
        'Authorization': 'token {}'.format(token),
        'Accept': 'application/json'
    }
    logging.info("github request token: {}".format(token))
    resp = requests.get(url=url, headers=headers)
    logging.info("github get response: {}".format(resp.text))
    data = resp.json()
    name = data.get('name', '')
    if not name:
        name = data.get('login', 'Github user')
    u_id = save_or_update_user(UserSource.github, data.get('id', ''),
                               name, data.get('avatar_url', ''), resp.text)
    set_session(conf, u_id, UserSource.github)
    return redirect_home()


@auth_bp.route('/callback/weibo')
@callback_auth('weibo')
@db_session
def callback_weibo():
    """处理weibo回调请求"""
    code = request.args.get('code', '')
    conf = current_app.config
    url = 'https://api.weibo.com/oauth2/access_token'
    params = {
        'client_id': conf['WEIBO_APP_KEY'],
        'client_secret': conf['WEIBO_APP_SECRET'],
        'grant_type': 'authorization_code',
        'redirect_uri': conf['WEIBO_REDIRECT_URI'],
        'code': code
    }
    logging.info("weibo request code {}".format(code))
    resp = requests.post(url=url, params=params, headers={'Accept': 'application/json'})
    logging.info("weibo get response: {}".format(resp.text))
    data = resp.json()
    if not data.get('access_token', ''):
        logging.warning('weibo get error response')
        return redirect('/')
    access_token = data.get('access_token', '')
    uid = data.get('uid', '')

    url = 'https://api.weibo.com/2/users/show.json'
    params = {
        'access_token': access_token,
        'uid': uid
    }
    logging.info("weibo request access_token: {}, uid: {}".format(access_token, uid))
    resp = requests.get(url=url, params=params, headers={'Accept': 'application/json'})
    if resp.status_code != 200:
        return redirect_home()
    logging.info("weibo get response: {}".format(resp.text))
    data = resp.json()
    u_id = save_or_update_user(UserSource.weibo, data.get('id', ''), data.get('name', ''),
                               data.get('profile_image_url', ''), resp.text)
    set_session(conf, u_id, UserSource.weibo)
    return redirect_home()


@auth_bp.route('/callback/weibo/cancel')
@db_session
def callback_weibo_cancel():
    """用户取消授权"""
    logging.warning(request.args)
    logging.warning(request.data)
    return {'hello': 'yes, i know'}


@auth_bp.route('/callback/google')
@callback_auth('google')
@db_session
def callback_google():
    """处理 google 回调请求"""
    code = request.args.get('code', '')
    error = request.args.get('error', '')
    conf = current_app.config
    if error:
        logging.warning("get error response")
        return redirect_home()

    url = 'https://oauth2.googleapis.com/token'
    params = {
        'code': code,
        'client_id': conf['GOOGLE_CLIENT_ID'],
        'client_secret': conf['GOOGLE_CLIENT_SECRET'],
        'redirect_uri': conf['GOOGLE_REDIRECT_URI'],
        'grant_type': 'authorization_code',
    }
    headers = {
        'Host': 'oauth2.googleapis.com',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    logging.info("google request code {}".format(code))
    resp = requests.post(url=url, params=params, headers=headers)
    logging.info("google get response: {}".format(resp.text))
    data = resp.json()
    access_token = data.get('access_token', '')
    if not access_token:
        logging.warning('google get error response')
        return redirect_home()

    url = 'https://www.googleapis.com/oauth2/v3/userinfo'
    # url = 'https://www.googleapis.com/auth/userinfo.profile'
    headers = {
        'Host': 'www.googleapis.com',
        'Authorization': 'Bearer {}'.format(access_token)
    }
    logging.info("google request access_token: {}".format(access_token))
    resp = requests.get(url=url, headers=headers)
    logging.info("google get response: {}".format(resp.text))
    if resp.status_code != 200:
        return redirect_home()
    data = resp.json()
    name = data.get('name', '')
    if not name:
        name = data.get('email', '')
    s_id = data.get('id', '')
    if not s_id:
        s_id = data.get('sub', '')
    u_id = save_or_update_user(UserSource.google, s_id, name,
                               data.get('picture', ''), resp.text)
    set_session(conf, u_id, UserSource.google)
    return redirect_home()
