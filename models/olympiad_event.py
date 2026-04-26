from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class OlympiadEvent(models.Model):
    _name = 'sp_olympiad.event'
    _description = 'Olympiad Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Event Name', required=True, tracking=True)
    year = fields.Integer(
        string='Year',
        required=True,
        tracking=True,
        help='Event year'
    )
    code_prefix = fields.Char(
        string='Code Prefix',
        required=True,
        default='OLY-',
        size=5,
        tracking=True,
        help="The prefix used to generate unique codes for projects in this event (e.g. OLY-)."
    )
    min_jury_per_project = fields.Integer(
        string='Min Jury Per Project',
        default=2,
        required=True,
        help='Minimum number of jury members required per project.',
    )
    best_stand_max_score = fields.Integer(
        string='Best Stand Max Score',
        default=10,
        required=True,
        help='Maximum score for best stand public voting.',
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
    medal_gold_min = fields.Integer(string='Gold Min', default=91, required=True)
    medal_silver_min = fields.Integer(string='Silver Min', default=81, required=True)
    medal_bronze_min = fields.Integer(string='Bronze Min', default=65, required=True)
    medal_hm_min = fields.Integer(string='Honorable Min', default=50, required=True)
    age_junior_min = fields.Integer(string='Junior Min Age', default=12, required=True)
    age_junior_max = fields.Integer(string='Junior Max Age', default=14, required=True)
    age_senior_min = fields.Integer(string='Senior Min Age', default=15, required=True)
    age_senior_max = fields.Integer(string='Senior Max Age', default=19, required=True)
    research_paper_deadline = fields.Date(
        string='Research Paper Deadline',
        help='Deadline for research paper submission'
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

    @api.constrains(
        'medal_gold_min',
        'medal_silver_min',
        'medal_bronze_min',
        'medal_hm_min',
    )
    def _check_medal_thresholds_order(self):
        for record in self:
            if not (
                record.medal_gold_min >= record.medal_silver_min >=
                record.medal_bronze_min >= record.medal_hm_min
            ):
                raise ValidationError(
                    'Medal thresholds must follow: Gold >= Silver >= Bronze >= Honorable Mention.'
                )

    @api.constrains(
        'age_junior_min',
        'age_junior_max',
        'age_senior_min',
        'age_senior_max',
    )
    def _check_age_boundaries(self):
        for record in self:
            if record.age_junior_min > record.age_junior_max:
                raise ValidationError('Junior minimum age cannot be greater than junior maximum age.')
            if record.age_senior_min > record.age_senior_max:
                raise ValidationError('Senior minimum age cannot be greater than senior maximum age.')
            if record.age_junior_max >= record.age_senior_min:
                raise ValidationError('Junior max age must be lower than senior min age.')

    @api.constrains('min_jury_per_project', 'best_stand_max_score')
    def _check_config_values(self):
        for record in self:
            if record.min_jury_per_project < 1:
                raise ValidationError('Min Jury Per Project must be at least 1.')
            if record.best_stand_max_score < 1:
                raise ValidationError('Best Stand Max Score must be at least 1.')
