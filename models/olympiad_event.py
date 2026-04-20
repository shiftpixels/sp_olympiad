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
    dates = fields.Date(string='Dates', required=True, tracking=True)
    date_end = fields.Date(string='End Date', required=True, tracking=True)
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
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id,
        help='Currency used for all event pricing fields.',
    )
    registration_fee = fields.Monetary(
        string='Registration Fee',
        currency_field='currency_id',
        default=200.0,
        help='Base fee per project registration.',
    )
    accommodation_fee = fields.Monetary(
        string='Accommodation Fee',
        currency_field='currency_id',
        default=50.0,
        help='Fee per person per night.',
    )
    excursion_fee = fields.Monetary(
        string='Excursion Fee',
        currency_field='currency_id',
        default=200.0,
        help='Excursion fee per person.',
    )
    accommodation_ids = fields.One2many(
        'sp_olympiad.event.accommodation',
        'event_id',
        string='Accommodation Dates',
        copy=True,
    )

    @api.constrains('code_prefix')
    def _check_code_prefix_length(self):
        for record in self:
            if record.code_prefix and len(record.code_prefix) > 5:
                raise ValidationError('Code Prefix cannot exceed 5 characters.')

    @api.constrains('dates', 'date_end')
    def _check_date_range(self):
        for record in self:
            if record.dates and record.date_end and record.dates > record.date_end:
                raise ValidationError("Start Date must be before or equal to End Date.")

    @api.constrains('state', 'date_end')
    def _check_finished_state(self):
        for record in self:
            if record.state == 'finished':
                if not record.date_end or record.date_end > fields.Date.today():
                    raise ValidationError("You cannot set the event to 'Finished' before its End Date has passed.")
