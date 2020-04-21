import logging
import os
from datetime import datetime
from urllib.parse import urlparse

from flask import session, redirect, Blueprint, request, render_template, jsonify, current_app
from pony.orm import commit, select, db_session
from qiniu import put_file, Auth

from db import Category, UserSite, UserSiteStatus, RSS, UserRSS
from util.tool import check_user, login_require, select_website, query_icon, redirect_home, download_icon_job, randstr

user_bp = Blueprint('user', __name__, template_folder='templates')

user_bp.before_request(check_user)


@user_bp.route('/<int:u_id>', methods=['GET'])
@login_require
def user_setting(u_id: int):
    """用户管理后台"""
    if not hasattr(request, 'user') or not request.user:
        logging.info("invalid request")
        return redirect('/')
    return render_template('user.html', page='info')


@user_bp.route('/<int:u_id>/category', methods=['GET'])
@login_require
def user_category(u_id: int):
    categories = Category.select(lambda x: x.user == request.user and not x.delete)[:]
    return render_template('user.html', page='category', categories=categories)


@user_bp.route('/<int:u_id>/category', methods=['POST'])
@login_require
def user_category_post(u_id: int):
    form = request.form
    logging.info('user {} data {}'.format(u_id, form))
    name = form.get('name', '')
    order = form.get('order', '')
    if not name or not order or not order.isdigit():
        return jsonify({'status': -1})
    order = int(order)
    if 1 > order or order > 1000:
        return jsonify({'status': -1})
    cate = Category(name=name, order=order, user=request.user)
    logging.info('user {} add new category {} {}'.format(u_id, cate.id, name))
    commit()
    return jsonify({'status': 1, 'id': cate.id})


@user_bp.route('/<int:u_id>/category', methods=['DELETE'])
@login_require
def user_category_delete(u_id: int):
    form = request.form
    logging.info('user {} delete data {}'.format(u_id, form))
    cate_id = form.get('id', '')
    if not cate_id or not cate_id.isdigit():
        return jsonify({'status': -1})
    cate_id = int(cate_id)
    cate = Category.select(lambda x: x.id == cate_id and x.user == request.user and not x.delete).first()
    if not cate:
        return jsonify({'status': -1})
    cate.delete = True
    logging.warning('user {} delete category {}'.format(u_id, cate.id))
    commit()
    return jsonify({'status': 1, 'id': cate.id})


@user_bp.route('/<int:u_id>/category', methods=['PUT'])
@login_require
def user_category_put(u_id: int):
    form = request.form
    logging.info('user {} update data {}'.format(u_id, form))
    cate_id = form.get('id', '')
    name = form.get('name', '')
    order = form.get('order', '')
    if not cate_id or not cate_id.isdigit() or not name or not order or not order.isdigit():
        return jsonify({'status': -1})
    order = int(order)
    if 1 > order or order > 1000:
        return jsonify({'status': -1})
    cate = Category.select(lambda x: x.id == cate_id and x.user == request.user and not x.delete).first()
    cate.name = name
    cate.order = order
    commit()
    logging.info('user {} update category {}'.format(u_id, cate.id))
    return jsonify({'status': 1, 'id': cate.id})


@user_bp.route('/<int:u_id>/website', methods=['GET'])
@login_require
def user_website(u_id: int):
    sites, categories = select_website()
    return render_template('user.html', page='website', sites=sites, categories=categories)


@user_bp.route('/<int:u_id>/website', methods=['POST'])
@login_require
def user_website_post(u_id: int):
    form = request.form
    logging.info('user {} post data {}'.format(u_id, form))
    cate_id = form.get('cate_id', '')
    name = form.get('name', '')
    url = form.get('url', '')
    order = form.get('order', '')
    type_ = form.get('type', '')

    if not name or not url or not order or not order.isdigit():
        return jsonify({'status': -1})
    order = int(order)
    if order > 1000 or order < 1:
        return jsonify({'status': -1})
    if not cate_id or not cate_id.isdigit():
        cate_id = None
        cate = None
    else:
        cate_id = int(cate_id)
        cate = Category.select(lambda x: x.user == request.user and x.id == cate_id and not x.delete).first()
        if not cate:
            return jsonify({'status': -1})
    try:
        icon = query_icon(urlparse(url).netloc)
    except Exception:
        icon = ''
    site = UserSite(name=name, url=url, user=request.user, icon=icon, cate=cate, order=order)
    commit()
    logging.info('user {} post site {}'.format(u_id, site.id))
    if not icon:
        logging.warning("icon not found, send to redis")
        download_icon_job(site.id)
    if type_ == 'index':
        return redirect_home()
    return jsonify({'status': 1, 'id': site.id})


@user_bp.route('/<int:u_id>/website', methods=['DELETE'])
@login_require
def user_website_delete(u_id: int):
    form = request.form
    logging.info('user {} delete data {}'.format(u_id, form))
    cate_id = form.get('id', '')
    if not cate_id or not cate_id.isdigit():
        return jsonify({'status': -1})
    cate_id = int(cate_id)
    site = UserSite.select(
        lambda x: x.id == cate_id and x.user == request.user and x.status == UserSiteStatus.normal).first()
    if not site:
        return jsonify({'status': -1})
    site.status = UserSiteStatus.delete
    site.delete_time = datetime.utcnow()
    commit()
    logging.warning('user {} delete website {}'.format(u_id, site.id))
    return jsonify({'status': 1, 'id': site.id})


@user_bp.route('/website/icon', methods=['POST'])
@login_require
def update_icon():
    """"""
    icon = request.files['icon']
    site_id = request.form.get('id', '')
    conf = current_app.config
    if not icon or not site_id:
        return ''
    filename = randstr(16)
    filepath = os.path.join(conf['ICON_DIR'], "{}.png".format(filename))
    icon.save(filepath)
    if not os.path.exists(filepath) or os.stat(filepath).st_size > 10 * 1024:
        return ''

    key = 'site/{}.png'.format(filename)
    q = Auth(conf['QINIU_ACCESS_KEY'], conf['QINIU_ACCESS_SECRET'])
    token = q.upload_token(conf['QINIU_BUCKET'], key, 60)
    ret, info = put_file(token, key, filepath)
    logging.info(info)
    site = UserSite.select(
        lambda x: x.id == site_id and x.user == request.user and x.status == UserSiteStatus.normal).first()
    if not site:
        return jsonify({'status': -1})
    site.icon = filename
    commit()

    return ''


@user_bp.route('/<int:u_id>/rss', methods=['GET'])
@login_require
def user_rss(u_id: int):
    user_rss = select((ur.id, ur.name, ur.rss.link) for ur in UserRSS
                      if ur.user == request.user and not ur.delete)[:]
    return render_template('user.html', page='rss', user_rss=user_rss)


@user_bp.route('/<int:u_id>/rss', methods=['POST'])
@login_require
@db_session
def user_rss_post(u_id: int):
    form = request.form
    logging.info('user {} post data {}'.format(u_id, form))
    name = form.get('name', '')
    url = form.get('url', '')
    if not name or not url:
        return jsonify({'status': -1})
    result = urlparse(url)
    if not result:
        return jsonify({'status': -1})
    rss = RSS.select(lambda x: x.link == url).first()
    if not rss:
        rss = RSS(link=url)
    ur = UserRSS(user=request.user, rss=rss, name=name)
    commit()
    logging.info('user {} post rss {}'.format(u_id, ur.id))
    return jsonify({'status': 1, 'id': ur.id})


@user_bp.route('/<int:u_id>/rss', methods=['DELETE'])
@login_require
def user_rss_delete(u_id: int):
    logging.info('user {} update data {}'.format(u_id, request.form))
    rss_id = request.form.get('id', '')
    if not rss_id or not rss_id.isdigit():
        return jsonify({'status': -1})
    ur = UserRSS.select(lambda x: x.id == int(rss_id) and x.user == request.user and not x.delete).first()
    if not ur:
        return jsonify({'status': -1})
    ur.delete = True
    ur.delete_time = datetime.utcnow()
    commit()
    logging.info('user {} delete rss {}'.format(u_id, rss_id))
    return jsonify({'status': 1, 'id': ur.id})


@user_bp.route('/logout', methods=['GET'])
def user_logout():
    """删除登录状态"""
    session.clear()
    return redirect('/')
