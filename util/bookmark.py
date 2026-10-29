import re

from pony.orm import select

from db import Tag


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


def get_or_create_tags(user, tag_names):
    name_keys = [name_key for _, name_key in tag_names]
    existing = select(t for t in Tag if t.user == user and t.name_key in name_keys)[:] if name_keys else []
    tags_by_key = {tag.name_key: tag for tag in existing}
    for name, name_key in tag_names:
        if name_key not in tags_by_key:
            tags_by_key[name_key] = Tag(name=name, name_key=name_key, user=user)
    return [tags_by_key[name_key] for _, name_key in tag_names]
