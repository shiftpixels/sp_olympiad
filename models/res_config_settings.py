from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    olympiad_name = fields.Char(
        string="Competition Name",
        config_parameter='sp_olympiad.olympiad_name',
    )
    category_max_participants_limit = fields.Integer(
        string="Category Max Participants Limit",
        default=10,
        config_parameter='sp_olympiad.category_max_participants_limit',
    )
    mentor_signup_enabled = fields.Boolean(
        string='Enable Mentor Signup',
        config_parameter='sp_olympiad.mentor_signup_enabled',
    )
    mentor_verification_enabled = fields.Boolean(
        string='Require Email Verification',
        config_parameter='sp_olympiad.mentor_verification_enabled',
        default=True,
    )
    
    # Rate limiting settings
    login_rate_limit_window = fields.Integer(
        string='Login Rate Limit Window (seconds)',
        default=600,
        config_parameter='sp_olympiad.login_rate_limit_window',
        help='Time window in seconds for login rate limiting',
    )
    login_rate_limit_ip = fields.Integer(
        string='Login Rate Limit IP',
        default=30,
        config_parameter='sp_olympiad.login_rate_limit_ip',
        help='Maximum login attempts per IP within time window',
    )
    login_rate_limit_email = fields.Integer(
        string='Login Rate Limit Email',
        default=10,
        config_parameter='sp_olympiad.login_rate_limit_email',
        help='Maximum login attempts per email within time window',
    )
    signup_rate_limit_window = fields.Integer(
        string='Signup Rate Limit Window (seconds)',
        default=600,
        config_parameter='sp_olympiad.signup_rate_limit_window',
        help='Time window in seconds for signup rate limiting',
    )
    signup_rate_limit_ip = fields.Integer(
        string='Signup Rate Limit IP',
        default=12,
        config_parameter='sp_olympiad.signup_rate_limit_ip',
        help='Maximum signup attempts per IP within time window',
    )
    signup_rate_limit_email = fields.Integer(
        string='Signup Rate Limit Email',
        default=3,
        config_parameter='sp_olympiad.signup_rate_limit_email',
        help='Maximum signup attempts per email within time window',
    )
    resend_rate_limit_window = fields.Integer(
        string='Resend Rate Limit Window (seconds)',
        default=600,
        config_parameter='sp_olympiad.resend_rate_limit_window',
        help='Time window in seconds for resend verification rate limiting',
    )
    resend_rate_limit_ip = fields.Integer(
        string='Resend Rate Limit IP',
        default=20,
        config_parameter='sp_olympiad.resend_rate_limit_ip',
        help='Maximum resend attempts per IP within time window',
    )
    resend_rate_limit_email = fields.Integer(
        string='Resend Rate Limit Email',
        default=5,
        config_parameter='sp_olympiad.resend_rate_limit_email',
        help='Maximum resend attempts per email within time window',
    )

    @api.constrains('category_max_participants_limit')
    def _check_category_max_participants_limit(self):
        for record in self:
            if record.category_max_participants_limit < 1:
                raise ValidationError('Category Max Participants Limit must be at least 1.')
