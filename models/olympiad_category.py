from odoo import _, api, fields, models
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

    @api.depends('max_participants')
    def _compute_is_solo(self):
        for record in self:
            record.is_solo = record.max_participants == 1

    @api.model
    def _get_max_participants_limit(self):
        limit_str = self.env['ir.config_parameter'].sudo().get_param(
            'sp_olympiad.category_max_participants_limit',
            default='10',
        )
        try:
            max_allowed = int(limit_str)
        except (TypeError, ValueError):
            max_allowed = 10
        return max(max_allowed, 1)

    @api.onchange('max_participants')
    def _onchange_max_participants_limit(self):
        max_allowed = self._get_max_participants_limit()
        if self.max_participants and self.max_participants > max_allowed:
            self.max_participants = max_allowed

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields=allfields, attributes=attributes)
        if 'max_participants' in res:
            max_allowed = self._get_max_participants_limit()
            res['max_participants']['help'] = (
                f'Maximum number of students allowed in a project for this category. '
                f'Current system limit: {max_allowed}. '
                'For higher values, ask an administrator to update '
                '"Category Max Participants Limit" in Olympiad General Settings.'
            )
        return res

    @api.constrains('max_participants')
    def _check_max_participants(self):
        max_allowed = self._get_max_participants_limit()
        for record in self:
            if record.max_participants < 1:
                raise ValidationError('Max Participants must be at least 1.')
            if record.max_participants > max_allowed:
                raise ValidationError(
                    f'Max Participants cannot be greater than {max_allowed}. '
                    'You can change this value in Olympiad General Settings.'
                )

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            if not record.code:
                continue
            duplicate = self.search(
                [('code', '=', record.code), ('id', '!=', record.id)],
                limit=1,
            )
            if duplicate:
                raise ValidationError('Category code must be unique!')

    def unlink(self):
        event_model = self.env['sp_olympiad.event'].sudo().with_context(active_test=False)
        for record in self:
            linked_event = event_model.search([('category_ids', 'in', record.id)], limit=1)
            if linked_event:
                raise ValidationError(
                    _(
                        "You cannot delete category '%(category)s' because it is used in event "
                        "'%(event)s'. Archive it instead."
                    )
                    % {
                        'category': record.display_name,
                        'event': linked_event.display_name,
                    }
                )
        return super().unlink()
