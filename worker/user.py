import logging
from collections import defaultdict

from flask import session, redirect, Blueprint, request, render_template, jsonify
from pony.orm import commit, select

from db import Category, UserSite, UserSiteStatus
from util.tool import check_user, login_require

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
    name = form.get('name', '')
    order = form.get('order', '')
    if not name or not order or not order.isdigit():
        return jsonify({'status': -1})
    order = int(order)
    if 1 > order or order > 1000:
        return jsonify({'status': -1})
    cate = Category(name=name, order=order, user=request.user)
    commit()
    return jsonify({'status': 1, 'id': cate.id})


@user_bp.route('/<int:u_id>/category', methods=['DELETE'])
@login_require
def user_category_delete(u_id: int):
    form = request.form
    cate_id = form.get('id', '')
    if not cate_id or not cate_id.isdigit():
        return jsonify({'status': -1})
    cate_id = int(cate_id)
    cate = Category.select(lambda x: x.id == cate_id and x.user == request.user and not x.delete).first()
    if not cate:
        return jsonify({'status': -1})
    cate.delete = True
    commit()
    return jsonify({'status': 1, 'id': cate.id})


@user_bp.route('/<int:u_id>/category', methods=['PUT'])
@login_require
def user_category_put(u_id: int):
    form = request.form
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
    return jsonify({'status': 1, 'id': cate.id})


@user_bp.route('/<int:u_id>/website', methods=['GET'])
@login_require
def user_website(u_id: int):
    sites = UserSite.select(lambda x: x.user == request.user and x.status == UserSiteStatus.normal)[:]
    categories = Category.select(lambda c: c.user == request.user and not c.delete).order_by(Category.order)[:]
    ss = defaultdict(list)
    for s in sites:
        key = s.cate.id if s.cate else ""
        ss[key].append(s)
    categories = list(categories)
    categories.insert(0, {"id": '', 'name': '常用网址', 'order': 0})
    return render_template('user.html', page='website', sites=ss, categories=categories)


@user_bp.route('/<int:u_id>/website', methods=['POST'])
@login_require
def user_website_post(u_id: int):
    form = request.form
    cate_id = form.get('cate_id', '')
    name = form.get('name', '')
    url = form.get('url', '')
    order = form.get('order', '')
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
    site = UserSite(name=name, url=url, user=request.user, cate=cate, order=order)
    commit()
    return jsonify({'status': 1, 'id': site.id})


@user_bp.route('/<int:u_id>/website', methods=['DELETE'])
@login_require
def user_website_delete(u_id: int):
    form = request.form
    cate_id = form.get('id', '')
    if not cate_id or not cate_id.isdigit():
        return jsonify({'status': -1})
    cate_id = int(cate_id)
    site = UserSite.select(
        lambda x: x.id == cate_id and x.user == request.user and x.status == UserSiteStatus.normal).first()
    if not site:
        return jsonify({'status': -1})
    site.status = UserSiteStatus.delete
    commit()
    return jsonify({'status': 1, 'id': site.id})


@user_bp.route('/<int:u_id>/rss', methods=['GET'])
@login_require
def user_rss(u_id: int):
    return render_template('user.html', page='rss')


@user_bp.route('/logout', methods=['GET'])
def user_logout():
    """删除登录状态"""
    session.clear()
    return redirect('/')
