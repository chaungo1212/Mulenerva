"""Utilities for interacting with Catalog metadata."""

def has_all_metadata(obj):
    try:
        retv = ('type' in obj and isinstance(obj['type'], str) and
                'title' in obj and isinstance(obj['title'], str) and
                'author' in obj and isinstance(obj['author'], str) and
                'genre' in obj and isinstance(obj['genre'], str) and
                'short_desc' in obj and isinstance(obj['short_desc'], str) and
                'long_desc' in obj and isinstance(obj['long_desc'], str) and
                'tags' in obj and isinstance(obj['tags'], list) and
                'is_requested' in obj and isinstance(obj['is_requested'], bool) and
                'is_available' in obj and isinstance(obj['is_available'], bool) and
                'previous_key' in obj and isinstance(obj['previous_key'], str) and
                'next_key' in obj and isinstance(obj['next_key'], str) and
                'size' in obj and isinstance(obj['size'], int) and
                'length' in obj and isinstance(obj['length'], int) and
                'time_stored' in obj and isinstance(obj['time_stored'], int) and
                'expiration' in obj and isinstance(obj['expiration'], int) and
                'thumbnail_key' in obj and isinstance(obj['thumbnail_key'], str) and
                'content_key' in obj and isinstance(obj['content_key'], str))
        return retv
    except Exception as e:
        return False

def has_required_metadata(obj):
    try:
        res =  ('type' in obj and isinstance(obj['type'], str) and
                'title' in obj and isinstance(obj['title'], str) and
                'author' in obj and isinstance(obj['author'], str) and
                'genre' in obj and isinstance(obj['genre'], str) and
                'short_desc' in obj and isinstance(obj['short_desc'], str) and
                'long_desc' in obj and isinstance(obj['long_desc'], str) and
                'tags' in obj and isinstance(obj['tags'], list) and
                'size' in obj and isinstance(obj['size'], int) and
                'length' in obj and isinstance(obj['length'], int) and
                'thumbnail_key' in obj and isinstance(obj['thumbnail_key'], str) and
                'content_key' in obj and isinstance(obj['content_key'], str))
        obj['tags'] = [tag.lower() for tag in obj['tags']]
        return res
    except Exception as e:
        return False

def populate_optional_fields(obj):
    if not has_required_metadata(obj):
        return
    obj['is_requested'] = False
    obj['is_available'] = False
    obj['previous_key'] = ''
    obj['next_key'] = ''
    obj['time_stored'] = 0
    obj['expiration'] = 0


SAMPLE_1 = {
    "type": "video",
    "title": "Making babies",
    "author": "Newton",
    "genre": "Biology",
    "short_desc": "Birds and bees",
    "long_desc": "Don't make me explain it.",
    "tags": ["gross", "ew", "bleh"],
    "is_requested": False,
    "is_available": False,
    "previous_key": "",
    "next_key": "",
    "size": 1,
    "length": 123,
    "time_stored": 0,
    "expiration": 0,
    "thumbnail_key": "",
    "content_key": ""
}
SAMPLE_2 = {
    "type": "video",
    "title": "Turn off the lights I'm watching back to the future.",
    "author": "Dance Gavin Dance",
    "genre": "Art",
    "short_desc": "This song shreds.",
    "long_desc": "I mean, this song really shreds. Like bro. Shreds.",
    "tags": ['rock', 'music', 'guitar'],
    "is_requested": False,
    "is_available": False,
    "previous_key": "",
    "next_key": "",
    "size": 1,
    "length": 123,
    "time_stored": 0,
    "expiration": 0,
    "thumbnail_key": "",
    "content_key": ""
}
SAMPLE_3 = {
    "type": "video",
    "title": "Down With The Sickness",
    "author": "Disturbed",
    "genre": "Art",
    "short_desc": "AH WAHAHAHA",
    "long_desc": "UHG UGH",
    "tags": ["yikes", "ears", "dying"],
    "is_requested": False,
    "is_available": False,
    "previous_key": "",
    "next_key": "",
    "size": 1,
    "length": 123,
    "time_stored": 0,
    "expiration": 0,
    "thumbnail_key": "",
    "content_key": ""
}

samples = [SAMPLE_1, SAMPLE_2, SAMPLE_3]
