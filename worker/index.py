from datetime import datetime, timedelta

from flask import render_template, Blueprint, request, current_app
from pony.orm import select, desc, raw_sql

from db import Page, UserRSS, RSS
from util.tool import check_user, select_website, redirect_home, guess_locale

page_bp = Blueprint('page', __name__, template_folder='templates')

page_bp.before_request(check_user)


@page_bp.route('/', methods=['GET'])
def index():
    """根据用户是否登录判断返回页面"""
    cl = guess_locale()
    if hasattr(request, 'user') and request.user:
        sites, categories = select_website()
        last_year = datetime.utcnow() - timedelta(days=365)
        pages = sorted(select(
            (p.page_id, p.title, p.link, p.publish_date, p.rss, ur.name) for ur in UserRSS for p in Page
            if ur.user == request.user and not ur.delete
            and p.publish_date > last_year and ur.rss == p.rss
        ), key=lambda x: x[3], reverse=True)
        return render_template('index.html', sites=sites, categories=categories, pages=pages, locale=cl)

    if cl == 'zh':
        return render_template('index.zh.html')
    if cl == 'ja':
        return render_template('index.ja.html')
    return render_template('index.en.html')


@page_bp.route('/locale/<lc>', methods=['GET'])
def locale(lc):
    """设置位置"""
    resp = redirect_home()
    resp.set_cookie('locale', lc, max_age=99999999)
    return resp
