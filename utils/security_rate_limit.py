# -*- coding: utf-8 -*-
import time
from collections import defaultdict, deque
from threading import Lock

from odoo.http import request


_RATE_LIMIT_CONFIG = {
    'login': {'window_seconds': 600, 'ip_limit': 30, 'email_limit': 10},
    'signup': {'window_seconds': 600, 'ip_limit': 12, 'email_limit': 3},
    'resend': {'window_seconds': 600, 'ip_limit': 20, 'email_limit': 5},
}

_ATTEMPT_BUCKETS = defaultdict(deque)
_BUCKET_LOCK = Lock()


def _normalize_email(email):
    return (email or '').strip().lower()


def _get_request():
    try:
        if request and request.httprequest:
            return request
    except Exception:
        return None
    return None


def _get_client_ip():
    req = _get_request()
    if not req:
        return 'unknown'

    headers = req.httprequest.headers
    forwarded_for = (headers.get('X-Forwarded-For') or '').split(',')[0].strip()
    real_ip = (headers.get('X-Real-IP') or '').strip()
    return forwarded_for or real_ip or req.httprequest.remote_addr or 'unknown'


def _iter_scope_keys(scope, email):
    config = _RATE_LIMIT_CONFIG.get(scope)
    if not config:
        return []

    keys = []
    ip = _get_client_ip()
    keys.append((f'{scope}:ip:{ip}', config['ip_limit']))
    normalized_email = _normalize_email(email)
    if normalized_email:
        keys.append((f'{scope}:email:{normalized_email}', config['email_limit']))
    return keys


def _prune_bucket(bucket, cutoff):
    while bucket and bucket[0] < cutoff:
        bucket.popleft()


def is_rate_limited(scope, email=None):
    config = _RATE_LIMIT_CONFIG.get(scope)
    if not config:
        return False

    now = time.time()
    cutoff = now - config['window_seconds']
    keys = _iter_scope_keys(scope, email)

    with _BUCKET_LOCK:
        for key, limit in keys:
            bucket = _ATTEMPT_BUCKETS[key]
            _prune_bucket(bucket, cutoff)
            if not bucket:
                _ATTEMPT_BUCKETS.pop(key, None)
                continue
            if len(bucket) >= limit:
                return True
    return False


def register_attempt(scope, email=None):
    config = _RATE_LIMIT_CONFIG.get(scope)
    if not config:
        return

    now = time.time()
    cutoff = now - config['window_seconds']
    keys = _iter_scope_keys(scope, email)

    with _BUCKET_LOCK:
        for key, _limit in keys:
            bucket = _ATTEMPT_BUCKETS[key]
            _prune_bucket(bucket, cutoff)
            bucket.append(now)


def clear_attempts(scope, email=None):
    keys = _iter_scope_keys(scope, email)
    with _BUCKET_LOCK:
        for key, _limit in keys:
            _ATTEMPT_BUCKETS.pop(key, None)

