import json
import logging
from datetime import datetime

from flask import current_app
from pony.orm import commit

from db import BookmarkAIStatus, UserAIConfig
from flask_app import redis


def enqueue_bookmark_ai(bookmark):
    bookmark.ai_error = ''
    bookmark.ai_update_time = datetime.utcnow()
    config = UserAIConfig.get(user=bookmark.user)
    if not config:
        bookmark.ai_status = BookmarkAIStatus.not_configured
        commit()
        return False
    bookmark.ai_status = BookmarkAIStatus.pending
    commit()
    payload = json.dumps({'bookmark_id': bookmark.id, 'url': bookmark.url})
    try:
        redis.rpush(current_app.config['REDIS_BOOKMARK_AI_QUEUE'], payload)
    except Exception:
        bookmark.ai_status = BookmarkAIStatus.failed
        bookmark.ai_error = 'AI task could not be queued.'
        bookmark.ai_update_time = datetime.utcnow()
        commit()
        logging.warning('Bookmark %s AI task could not be queued.', bookmark.id)
        return False
    return True
