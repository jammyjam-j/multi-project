import threading
import time

_cache = {}
_cache_lock = threading.Lock()


def cache_get(key):
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        if time.time() > entry['expires_at']:
            _cache.pop(key, None)
            return None
        return entry['value']


def cache_set(key, value, ttl=30):
    with _cache_lock:
        _cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
        }


def cache_invalidate(pattern):
    """Remove keys that start with the pattern."""
    with _cache_lock:
        keys_to_remove = [key for key in _cache if key.startswith(pattern)]
        for key in keys_to_remove:
            _cache.pop(key, None)
