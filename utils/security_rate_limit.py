# -*- coding: utf-8 -*-
import time
from collections import defaultdict, deque
from threading import Lock

from odoo.http import request


_ATTEMPT_BUCKETS = defaultdict(deque)
_BUCKET_LOCK = Lock()


def _get_rate_limit_config(scope):
    """Get rate limit configuration from system parameters."""
    try:
        env = request.env if request else None
        if not env:
            # Fallback to default values if no environment available
            return _get_default_config(scope)
        
        config = {}
        if scope == 'login':
            config = {
                'window_seconds': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.login_rate_limit_window', '600')),
                'ip_limit': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.login_rate_limit_ip', '30')),
                'email_limit': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.login_rate_limit_email', '10')),
            }
        elif scope == 'signup':
            config = {
                'window_seconds': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.signup_rate_limit_window', '600')),
                'ip_limit': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.signup_rate_limit_ip', '12')),
                'email_limit': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.signup_rate_limit_email', '3')),
            }
        elif scope == 'resend':
            config = {
                'window_seconds': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.resend_rate_limit_window', '600')),
                'ip_limit': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.resend_rate_limit_ip', '20')),
                'email_limit': int(env['ir.config_parameter'].sudo().get_param(
                    'sp_olympiad.resend_rate_limit_email', '5')),
            }
        else:
            return _get_default_config(scope)
        
        # Validate and ensure minimum values
        config['window_seconds'] = max(config['window_seconds'], 60)
        config['ip_limit'] = max(config['ip_limit'], 1)
        config['email_limit'] = max(config['email_limit'], 1)
        
        return config
    except Exception:
        return _get_default_config(scope)


def _get_default_config(scope):
    """Get default rate limit configuration as fallback."""
    default_configs = {
        'login': {'window_seconds': 600, 'ip_limit': 30, 'email_limit': 10},
        'signup': {'window_seconds': 600, 'ip_limit': 12, 'email_limit': 3},
        'resend': {'window_seconds': 600, 'ip_limit': 20, 'email_limit': 5},
    }
    return default_configs.get(scope, {})


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
    config = _get_rate_limit_config(scope)
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
    config = _get_rate_limit_config(scope)
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
    config = _get_rate_limit_config(scope)
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

