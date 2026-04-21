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

    @api.constrains('category_max_participants_limit')
    def _check_category_max_participants_limit(self):
        for record in self:
            if record.category_max_participants_limit < 1:
                raise ValidationError('Category Max Participants Limit must be at least 1.')
