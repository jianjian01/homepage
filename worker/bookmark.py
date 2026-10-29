import re
from datetime import datetime
from urllib.parse import urlparse

from flask import Blueprint, jsonify, redirect, request, url_for
from pony.orm import commit, count, db_session, desc, select

from db import Bookmark, BookmarkStatus, Tag
from util.tool import check_user, login_require

bookmark_bp = Blueprint('bookmark', __name__, template_folder='templates')
bookmark_bp.before_request(check_user)

PER_PAGE = 20


def parse_tag_names(value):
    names = []
    seen = set()
    for item in re.split(r'[,，]', value):
        name = item.strip()
        if not name:
            continue
        if len(name) > 30:
            raise ValueError('Each tag must be at most 30 characters.')
        name_key = name.casefold()
        if name_key in seen:
            continue
        seen.add(name_key)
        names.append((name, name_key))
    if len(names) > 10:
        raise ValueError('A bookmark can have at most 10 tags.')
    return names


def validate_bookmark_form():
    title = request.form.get('title', '').strip()
    url = request.form.get('url', '').strip()
    if not title or len(title) > 200:
        return None, None, None, (jsonify({'status': -1, 'message': 'Title is required and must be at most 200 characters.'}), 400)
    try:
        parsed = urlparse(url)
        valid_url = parsed.scheme in ('http', 'https') and bool(parsed.netloc) and bool(parsed.hostname)
    except ValueError:
        valid_url = False
    if len(url) > 2048 or not valid_url:
        return None, None, None, (jsonify({'status': -1, 'message': 'A valid HTTP or HTTPS URL of at most 2048 characters is required.'}), 400)
    try:
        tag_names = parse_tag_names(request.form.get('tags', ''))
    except ValueError as exc:
        return None, None, None, (jsonify({'status': -1, 'message': str(exc)}), 400)
    return title, url, tag_names, None


def get_or_create_tags(tag_names):
    name_keys = [name_key for _, name_key in tag_names]
    existing = select(t for t in Tag if t.user == request.user and t.name_key in name_keys)[:] if name_keys else []
    tags_by_key = {tag.name_key: tag for tag in existing}
    for name, name_key in tag_names:
        if name_key not in tags_by_key:
            tags_by_key[name_key] = Tag(name=name, name_key=name_key, user=request.user)
    return [tags_by_key[name_key] for _, name_key in tag_names]


def bookmark_context():
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    query_string = request.args.get('q', '').strip()[:100]
    tag_id = request.args.get('tag', 0, type=int)
    selected_tag = Tag.get(id=tag_id, user=request.user) if tag_id else None

    query = select(b for b in Bookmark if b.user == request.user and b.status == BookmarkStatus.normal)
    total_all = query.count()
    if selected_tag:
        query = select(b for b in Bookmark for tag in b.tags
                       if b.user == request.user and b.status == BookmarkStatus.normal and tag == selected_tag)
    if query_string:
        keyword = query_string.casefold()
        query = query.filter(lambda b: keyword in b.title.lower() or keyword in b.url.lower())

    total = query.count()
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages)
    bookmarks = query.order_by(desc(Bookmark.create_time), desc(Bookmark.id)).page(page, PER_PAGE)
    tags = select((tag.id, tag.name, count(b)) for tag in Tag for b in tag.bookmarks
                  if tag.user == request.user and b.status == BookmarkStatus.normal)
    tags = sorted(tags, key=lambda item: (-item[2], item[1].casefold()))
    return {
        'bookmarks': bookmarks,
        'page': page,
        'total_pages': total_pages,
        'total': total,
        'total_all': total_all,
        'tags': tags,
        'selected_tag': selected_tag,
        'query_string': query_string,
    }


@bookmark_bp.route('/', methods=['GET'])
@login_require
def index():
    args = request.args.to_dict()
    args['view'] = 'bookmarks'
    return redirect(url_for('page.index', **args))


@bookmark_bp.route('/', methods=['POST'])
@login_require
@db_session
def create():
    title, url, tag_names, error = validate_bookmark_form()
    if error:
        return error
    bookmark = Bookmark(title=title, url=url, user=request.user)
    bookmark.tags = get_or_create_tags(tag_names)
    commit()
    return jsonify({'status': 1, 'id': bookmark.id}), 201


@bookmark_bp.route('/<int:bookmark_id>', methods=['PUT'])
@login_require
@db_session
def update(bookmark_id):
    title, url, tag_names, error = validate_bookmark_form()
    if error:
        return error
    bookmark = Bookmark.select(
        lambda b: b.id == bookmark_id and b.user == request.user and b.status == BookmarkStatus.normal).first()
    if not bookmark:
        return jsonify({'status': -1, 'message': 'Bookmark not found.'}), 404
    bookmark.title = title
    bookmark.url = url
    bookmark.tags = get_or_create_tags(tag_names)
    bookmark.update_time = datetime.utcnow()
    commit()
    return jsonify({'status': 1, 'id': bookmark.id})


@bookmark_bp.route('/<int:bookmark_id>', methods=['DELETE'])
@login_require
@db_session
def delete(bookmark_id):
    bookmark = Bookmark.select(
        lambda b: b.id == bookmark_id and b.user == request.user and b.status == BookmarkStatus.normal).first()
    if not bookmark:
        return jsonify({'status': -1, 'message': 'Bookmark not found.'}), 404
    bookmark.status = BookmarkStatus.delete
    bookmark.delete_time = datetime.utcnow()
    commit()
    return jsonify({'status': 1, 'id': bookmark.id})
