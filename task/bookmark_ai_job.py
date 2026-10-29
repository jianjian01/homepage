import json
import logging
import time
from datetime import datetime
from types import SimpleNamespace

from pony.orm import db_session, select
from redis import Redis

from config import Config
from db import Bookmark, BookmarkAIStatus, BookmarkStatus, Tag, UserAIConfig, db
from util.bookmark import get_or_create_tags
from util.bookmark_ai import MIN_TEXT_CHARS, BookmarkAIError, fetch_page, generate_content_metadata


def finish_without_content(bookmark_id, url):
    with db_session:
        bookmark = Bookmark.get(id=bookmark_id)
        if not bookmark or bookmark.status != BookmarkStatus.normal or bookmark.url != url:
            return
        bookmark.summary = ''
        bookmark.ai_status = BookmarkAIStatus.no_content
        bookmark.ai_error = ''
        bookmark.ai_update_time = datetime.utcnow()


def finish_with_error(bookmark_id, url):
    with db_session:
        bookmark = Bookmark.get(id=bookmark_id)
        if not bookmark or bookmark.status != BookmarkStatus.normal or bookmark.url != url:
            return
        bookmark.ai_status = BookmarkAIStatus.failed
        bookmark.ai_error = 'AI processing failed. Please retry.'
        bookmark.ai_update_time = datetime.utcnow()


def handle(payload):
    bookmark_id = payload.get('bookmark_id')
    url = payload.get('url')
    if not isinstance(bookmark_id, int) or not isinstance(url, str):
        return
    with db_session:
        bookmark = Bookmark.get(id=bookmark_id)
        if (not bookmark or bookmark.status != BookmarkStatus.normal or bookmark.url != url
                or bookmark.ai_status != BookmarkAIStatus.pending):
            return
        config = UserAIConfig.get(user=bookmark.user)
        if not config:
            bookmark.ai_status = BookmarkAIStatus.not_configured
            bookmark.ai_update_time = datetime.utcnow()
            return
        bookmark.ai_status = BookmarkAIStatus.processing
        bookmark.ai_update_time = datetime.utcnow()
        title = bookmark.title
        existing_tags = select(t.name for t in Tag if t.user == bookmark.user)[:100]
        config_data = SimpleNamespace(provider=config.provider, model=config.model, api_key=config.api_key)
    try:
        _, page_title, text = fetch_page(url)
        if len(text) < MIN_TEXT_CHARS:
            finish_without_content(bookmark_id, url)
            return
        result = generate_content_metadata(page_title or title, text, existing_tags, config_data,
                                           Config.AI_CONFIG_ENCRYPTION_KEY)
        if not result['has_content']:
            finish_without_content(bookmark_id, url)
            return
        with db_session:
            bookmark = Bookmark.get(id=bookmark_id)
            if (not bookmark or bookmark.status != BookmarkStatus.normal or bookmark.url != url
                    or bookmark.ai_status != BookmarkAIStatus.processing):
                return
            remaining = max(0, 3 - len(bookmark.tags))
            tag_names = [(name, name.casefold()) for name in result['tags'][:remaining]]
            existing_keys = {tag.name_key for tag in bookmark.tags}
            for tag in get_or_create_tags(bookmark.user, tag_names):
                if tag.name_key not in existing_keys:
                    bookmark.tags.add(tag)
                    existing_keys.add(tag.name_key)
            bookmark.summary = result['summary']
            bookmark.ai_status = BookmarkAIStatus.success
            bookmark.ai_error = ''
            bookmark.ai_update_time = datetime.utcnow()
    except Exception as exc:
        logging.warning('Bookmark %s AI processing failed: %s', bookmark_id, type(exc).__name__)
        finish_with_error(bookmark_id, url)


def main():
    redis = Redis.from_url(Config.REDIS_URL)
    queue = Config.REDIS_BOOKMARK_AI_QUEUE
    logging.info('Listening on %s', queue)
    while True:
        item = redis.brpop(queue, timeout=5)
        if not item:
            continue
        try:
            payload = json.loads(item[1])
            if isinstance(payload, dict):
                handle(payload)
        except (TypeError, ValueError) as exc:
            logging.warning('Invalid bookmark AI task: %s', type(exc).__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    db.bind(**Config.PONY)
    db.generate_mapping()
    while True:
        try:
            main()
        except Exception as exc:
            logging.warning('Bookmark AI worker reconnecting after %s', type(exc).__name__)
            time.sleep(5)
