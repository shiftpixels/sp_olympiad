from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class MentorSignupController(http.Controller):

    @http.route(['/mentor/signup'], type='http', auth='public', website=True)
    def mentor_signup(self, **kwargs):
        """Render the mentor signup form."""
        # Redirect already logged in users to dashboard
        if request.env.user != request.env.ref('base.public_user'):
            # If user is admin or already a mentor, redirect to dashboard
            if request.env.user.has_group('base.group_system') or request.env.user.has_group('sp_olympiad.group_sp_olympiad_mentor'):
                return request.redirect('/my/olympiad')
            # For regular logged in users, show mentor signup
            countries = request.env['res.country'].sudo().search([])
            return request.render('sp_olympiad.mentor_signup_page', {
                'countries': countries,
                'success': kwargs.get('success'),
                'error': kwargs.get('error'),
            })

        countries = request.env['res.country'].sudo().search([])
        return request.render('sp_olympiad.mentor_signup_page', {
            'countries': countries,
            'success': kwargs.get('success'),
            'error': kwargs.get('error'),
        })

    @http.route(['/mentor/submit'], type='http', auth='public', methods=['POST'], csrf=False)
    def mentor_submit(self, **post):
        """Process mentor registration."""
        # Get form values
        name = post.get('name')
        email = post.get('email')
        password = post.get('password')
        country_id = post.get('country_id')
        branch = post.get('branch')
        phone = post.get('phone')

        # Validation
        if not all([name, email, password]):
            return request.render('sp_olympiad.mentor_signup_page', {
                'countries': request.env['res.country'].sudo().search([]),
                'error': _('Please fill in all required fields.'),
                'success': None,
                'form_data': post,
            })

        if len(password) < 8:
            return request.render('sp_olympiad.mentor_signup_page', {
                'countries': request.env['res.country'].sudo().search([]),
                'error': _('Password must be at least 8 characters long.'),
                'success': None,
                'form_data': post,
            })

        # Check if user already exists
        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return request.render('sp_olympiad.mentor_signup_page', {
                'countries': request.env['res.country'].sudo().search([]),
                'error': _('This email is already registered.'),
                'success': None,
                'form_data': post,
            })

        # Check if mentor already exists
        existing_mentor = request.env['sp_olympiad.mentor'].sudo().search([('email', '=', email)], limit=1)
        if existing_mentor:
            return request.render('sp_olympiad.mentor_signup_page', {
                'countries': request.env['res.country'].sudo().search([]),
                'error': _('This email is already registered as a mentor.'),
                'success': None,
                'form_data': post,
            })

        try:
            # Create res.user
            user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'email': email,
                'password': password,
            })

            # Add to mentor group
            mentor_group = request.env.ref('sp_olympiad.group_sp_olympiad_mentor', raise_if_not_found=False)
            if mentor_group and hasattr(user, 'groups_id'):
                user.write({'groups_id': [(4, mentor_group.id)]})

            # Create mentor profile
            mentor = request.env['sp_olympiad.mentor'].sudo().create({
                'name': name,
                'email': email,
                'user_id': user.id,
                'country_id': country_id or False,
                'branch': branch,
                'phone': phone,
                'verified': False,  # Default - needs email verification
            })

            # Generate verification token
            mentor.generate_verification_token()
            mentor.send_verification_email()

            _logger.info('Mentor registered: %s (%s)', name, email)

            # Redirect with success message
            return request.redirect('/mentor/signup?success=1')

        except Exception as e:
            _logger.error('Mentor registration error: %s', str(e))
            return request.render('sp_olympiad.mentor_signup_page', {
                'countries': request.env['res.country'].sudo().search([]),
                'error': _('Registration failed. Please try again later.'),
                'success': None,
                'form_data': post,
            })

    @http.route(['/mentor/verify/<token>'], type='http', auth='public', website=True)
    def mentor_verify(self, token=None, **kwargs):
        """Verify mentor email with token."""
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

        # Verify email
        if mentor.verify_email(token):
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': True,
                'message': _('Email verified successfully! You can now log in.'),
            })
        else:
            return request.render('sp_olympiad.mentor_verify_page', {
                'success': False,
                'error': _('Verification failed. Please try again.'),
            })

    @http.route(['/mentor/resend-verify'], type='http', auth='public', methods=['POST'], csrf=False)
    def mentor_resend_verify(self, **post):
        """Resend verification email."""
        email = post.get('email')
        if not email:
            return request.redirect('/mentor/signup?error=1')

        mentor = request.env['sp_olympiad.mentor'].sudo().search([('email', '=', email)], limit=1)
        if mentor and not mentor.verified:
            mentor.generate_verification_token()
            mentor.send_verification_email()
            return request.redirect('/mentor/signup?success=1&resend=1')

        return request.redirect('/mentor/signup?error=1')
