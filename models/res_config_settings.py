from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    olympiad_name = fields.Char(
        string="Competition Name",
        config_parameter='sp_olympiad_core.olympiad_name',
        help="Global name for the Olympiad competition."
    )
    category_max_participants_limit = fields.Integer(
        string="Category Max Participants Limit",
        default=10,
        config_parameter='sp_olympiad.category_max_participants_limit',
        help="Maximum allowed value for category Max Participants.",
    )

    @api.constrains('category_max_participants_limit')
    def _check_category_max_participants_limit(self):
        for record in self:
            if record.category_max_participants_limit < 1:
                raise ValidationError('Category Max Participants Limit must be at least 1.')
