from odoo import api, fields, models
from odoo.exceptions import ValidationError

class OlympiadCategory(models.Model):
    _name = 'sp_olympiad.category'
    _description = 'Olympiad Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, help="Short code for this category (e.g. ENV, BIO)")
    max_participants = fields.Integer(
        string='Max Participants',
        default=3,
        required=True,
        help='Maximum number of students allowed in a project for this category.',
    )
    is_solo = fields.Boolean(
        string='Solo Category',
        compute='_compute_is_solo',
        store=True,
        readonly=True,
        help='Automatically true when Max Participants is 1.',
    )
    sequence = fields.Integer(default=10, help="Determines the display order in the list and on the website (lower numbers appear first).")
    image = fields.Image(string='Category Image', max_width=512, max_height=512)
    description = fields.Html(string='Web Description', translate=True)
    criteria = fields.Html(string='Evaluation Criteria', translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Category code must be unique!')
    ]

    @api.depends('max_participants')
    def _compute_is_solo(self):
        for record in self:
            record.is_solo = record.max_participants == 1

    @api.constrains('max_participants')
    def _check_max_participants(self):
        for record in self:
            if record.max_participants < 1:
                raise ValidationError('Max Participants must be at least 1.')
