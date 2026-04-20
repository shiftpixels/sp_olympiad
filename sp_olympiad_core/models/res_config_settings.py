from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    olympiad_name = fields.Char(
        string="Competition Name",
        config_parameter='sp_olympiad_core.olympiad_name',
        help="Global name for the Olympiad competition."
    )
