from flask import render_template, Blueprint, request

from util.tool import check_user, select_website

page_bp = Blueprint('page', __name__, template_folder='templates')

page_bp.before_request(check_user)


@page_bp.route('/', methods=['GET'])
def index():
    """根据用户是否登录判断返回页面"""
    if hasattr(request, 'user') and request.user:
        sites, categories = select_website()
    else:
        sites, categories = None, None
    return render_template('index.html', sites=sites, categories=categories)
