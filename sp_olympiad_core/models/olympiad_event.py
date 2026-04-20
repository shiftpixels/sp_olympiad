from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class OlympiadEvent(models.Model):
    _name = 'sp_olympiad.event'
    _description = 'Olympiad Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Event Name', required=True, tracking=True)
    code_prefix = fields.Char(
        string='Code Prefix',
        required=True,
        default='OLY-',
        size=5,
        tracking=True,
        help="The prefix used to generate unique codes for projects in this event (e.g. OLY-)."
    )
    date_start = fields.Date(string='Start Date', tracking=True)
    date_end = fields.Date(string='End Date', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Active'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    category_ids = fields.Many2many(
        'sp_olympiad.category',
        string='Categories',
        help="Categories active for this event."
    )

    @api.constrains('code_prefix')
    def _check_code_prefix_length(self):
        for record in self:
            if record.code_prefix and len(record.code_prefix) > 5:
                raise ValidationError('Code Prefix cannot exceed 5 characters.')

    @api.constrains('state', 'date_end')
    def _check_finished_state(self):
        for record in self:
            if record.state == 'finished':
                if not record.date_end or record.date_end > fields.Date.today():
                    raise ValidationError("You cannot set the event to 'Finished' before its End Date has passed.")


