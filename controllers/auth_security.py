# -*- coding: utf-8 -*-
from urllib.parse import urlencode

from odoo import _, http
from odoo.addons.web.controllers.home import Home
from odoo.http import request

from ..utils.security_rate_limit import clear_attempts, is_rate_limited, register_attempt


class OlympiadAuthSecurityController(Home):

    @staticmethod
    def _generic_login_error_message():
        return _(
            'Login failed. Possible reasons: invalid credentials, email not yet verified, '
            'inactive account, or a temporary security lock.'
        )

    @http.route()
    def web_login(self, *args, **kw):
        login = (kw.get('login') or request.params.get('login') or '').strip().lower()
        is_post = request.httprequest.method == 'POST'
        redirect_target = kw.get('redirect')

        if is_post and is_rate_limited('login', email=login):
            params = {'login_blocked': 1}
            if redirect_target:
                params['redirect'] = redirect_target
            return request.redirect('/web/login?%s' % urlencode(params))

        response = super().web_login(*args, **kw)

        qcontext = getattr(response, 'qcontext', None)
        if not isinstance(qcontext, dict):
            if is_post and request.session.uid:
                clear_attempts('login', email=login)
            return response

        has_error = bool(qcontext.get('error')) or bool(kw.get('login_blocked'))

        if has_error:
            if is_post:
                register_attempt('login', email=login)
            qcontext['error'] = self._generic_login_error_message()
        elif is_post:
            clear_attempts('login', email=login)

        return response
