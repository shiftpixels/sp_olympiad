from odoo import http, _
from odoo.http import request
import logging

from ..utils.security_rate_limit import is_rate_limited, register_attempt

_logger = logging.getLogger(__name__)


class MentorSignupController(http.Controller):

    @staticmethod
    def _get_bool_param(key, default=False):
        value = request.env['ir.config_parameter'].sudo().get_param(
            key,
            '1' if default else '0'
        )
        return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}

    @staticmethod
    def _generic_signup_notice():
        return _('If the provided email is eligible, you will receive an email with next steps.')

    @staticmethod
    def _generic_resend_notice():
        return _('If the provided email exists and is pending verification, a new verification email has been sent.')

    @staticmethod
    def _rate_limit_error():
        return _('Too many attempts. Please wait a few minutes and try again.')

    def _render_signup(self, **kwargs):
        countries = request.env['res.country'].sudo().search([])
        return request.render('sp_olympiad.mentor_signup_page', {
            'countries': countries,
            'success': kwargs.get('success'),
            'error': kwargs.get('error'),
            'form_data': kwargs.get('form_data'),
            'success_message': kwargs.get('success_message'),
        })

    @http.route(['/mentor/signup'], type='http', auth='public', website=True)
    def mentor_signup(self, **kwargs):
        """Render the mentor signup form."""
        if not self._get_bool_param('sp_olympiad.mentor_signup_enabled', default=True):
            return request.not_found()

        if request.env.user != request.env.ref('base.public_user'):
            if request.env.user.has_group('base.group_system') or request.env.user.has_group('sp_olympiad.group_sp_olympiad_mentor'):
                return request.redirect('/my/olympiad')

        success = kwargs.get('success')
        resend = kwargs.get('resend')
        verified = kwargs.get('verified')
        generic_notice = kwargs.get('generic_notice')
        error_code = kwargs.get('error')

        success_message = None
        if success:
            if resend:
                success_message = self._generic_resend_notice()
            elif generic_notice:
                success_message = self._generic_signup_notice()
            elif verified:
                success_message = _('Registration completed successfully. You can log in now.')
            else:
                success_message = _('Your registration has been submitted. Please check your email to verify your account.')

        error_message = None
        if error_code == 'rate_limit':
            error_message = self._rate_limit_error()
        elif error_code:
            error_message = _('Request could not be completed. Please try again.')

        return self._render_signup(
            success=success,
            error=error_message,
            success_message=success_message,
        )

    @http.route(['/mentor/submit'], type='http', auth='public', methods=['POST'])
    def mentor_submit(self, **post):
        """Process mentor registration."""
        if not self._get_bool_param('sp_olympiad.mentor_signup_enabled', default=True):
            return request.not_found()

        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip().lower()
        password = post.get('password') or ''
        country_id = post.get('country_id')
        country_id_int = int(country_id) if country_id and country_id.isdigit() else False
        branch = (post.get('branch') or '').strip()
        phone = (post.get('phone') or '').strip()
        whatsapp = (post.get('whatsapp') or '').strip()

        form_data = {
            'name': name,
            'email': email,
            'country_id': country_id_int,
            'branch': branch,
            'phone': phone,
            'whatsapp': whatsapp,
        }

        if not all([name, email, password]):
            return self._render_signup(
                error=_('Please fill in all required fields.'),
                form_data=form_data,
            )

        if country_id_int:
            country_exists = request.env['res.country'].sudo().search_count([('id', '=', country_id_int)])
            if not country_exists:
                return self._render_signup(
                    error=_('Invalid country selected.'),
                    form_data=form_data,
                )

        if len(password) < 8:
            return self._render_signup(
                error=_('Password must be at least 8 characters long.'),
                form_data=form_data,
            )

        if is_rate_limited('signup', email=email):
            return self._render_signup(
                error=self._rate_limit_error(),
                form_data=form_data,
            )
        register_attempt('signup', email=email)

        verification_enabled = self._get_bool_param('sp_olympiad.mentor_verification_enabled', default=True)

        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        existing_mentor = request.env['sp_olympiad.mentor'].sudo().search([('email', '=', email)], limit=1)
        if existing_user or existing_mentor:
            return request.redirect('/mentor/signup?success=1&generic_notice=1')

        try:
            with request.env.cr.savepoint():
                mentor_group = request.env.ref('sp_olympiad.group_sp_olympiad_mentor', raise_if_not_found=False)
                portal_group = request.env.ref('base.group_portal', raise_if_not_found=False)

                initial_groups = []
                if portal_group:
                    initial_groups.append(portal_group.id)
                if not verification_enabled and mentor_group:
                    initial_groups.append(mentor_group.id)

                user = request.env['res.users'].sudo().with_context(no_reset_password=True).create({
                    'name': name,
                    'login': email,
                    'email': email,
                    'password': password,
                    'phone': phone,
                    'active': not verification_enabled,
                    'group_ids': [(6, 0, initial_groups)],
                })

                # We don't need this anymore as we set group_ids above
                # if not verification_enabled and mentor_group and hasattr(user, 'group_ids'):
                #     user.sudo().write({
                #         'group_ids': [(4, mentor_group.id)],
                #     })

                mentor_values = {
                    'name': name,
                    'email': email,
                    'user_id': user.id,
                    'country_id': country_id_int,
                    'branch': branch,
                    'phone': phone,
                    'whatsapp': whatsapp,
                }
                if not verification_enabled:
                    mentor_values['verified'] = True

                mentor = request.env['sp_olympiad.mentor'].sudo().create(mentor_values)

                if verification_enabled:
                    mentor.generate_verification_token()
                    mentor.send_verification_email()

            _logger.info(
                'Mentor registered: %s (%s) - active=%s, verified=%s',
                name,
                email,
                user.active,
                mentor.verified,
            )

            if verification_enabled:
                return request.redirect('/mentor/signup?success=1')
            return request.redirect('/mentor/signup?success=1&verified=1')

        except Exception as exc:
            _logger.exception('Mentor registration error: %s', exc)
            return self._render_signup(
                error=_('Registration failed. Please try again later.'),
                form_data=form_data,
            )

    @http.route(['/mentor/verify/<token>'], type='http', auth='public', website=True)
    def mentor_verify(self, token=None, **kwargs):
        """Verify mentor email with token."""
        if not self._get_bool_param('sp_olympiad.mentor_verification_enabled', default=True):
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': True,
                'message': _('Email verification is not required for mentor accounts.'),
            })

        if not token:
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': False,
                'error': _('No verification token provided.'),
            })

        mentor = request.env['sp_olympiad.mentor'].sudo().search(
            [('verification_token', '=', token)],
            limit=1
        )

        if not mentor:
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': False,
                'error': _('Invalid verification token.'),
            })

        if mentor.verified:
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': True,
                'message': _('Email already verified. You can log in now.'),
            })

        if mentor.verification_token_expired():
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': False,
                'error': _('Verification token has expired. Please request a new one.'),
                'mentor': mentor,
            })

        if mentor.verify_email(token):
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': True,
                'message': _('Email verified successfully! You can now log in.'),
            })

        return request.render('sp_olympiad.mentor_verify_page', {
            'success': False,
            'error': _('Verification failed. Please try again.'),
        })

    @http.route(['/mentor/resend-verify'], type='http', auth='public', methods=['POST'])
    def mentor_resend_verify(self, **post):
        """Resend verification email."""
        if not self._get_bool_param('sp_olympiad.mentor_verification_enabled', default=True):
            return request.redirect('/mentor/signup?success=1&generic_notice=1')

        email = (post.get('email') or '').strip().lower()
        if is_rate_limited('resend', email=email):
            return request.redirect('/mentor/signup?error=rate_limit')
        register_attempt('resend', email=email)

        if email:
            mentor = request.env['sp_olympiad.mentor'].sudo().search([('email', '=', email)], limit=1)
            if mentor and not mentor.verified:
                mentor.generate_verification_token()
                mentor.send_verification_email()

        return request.redirect('/mentor/signup?success=1&resend=1')
