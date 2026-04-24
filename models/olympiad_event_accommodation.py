from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OlympiadEventAccommodation(models.Model):
    _name = 'sp_olympiad.event.accommodation'
    _description = 'Olympiad Event Accommodation Date'
    _order = 'sequence, date, id'

    @api.ondelete(at_uninstall=False)
    def _unlink_guard(self):
        for record in self:
            if record.date and record.date < fields.Date.today():
                raise ValidationError("Cannot delete past accommodation dates for data integrity.")

    @api.model
    def _default_date(self):
        if self.env.context.get('default_date'):
            return self.env.context.get('default_date')
        event_id = self.env.context.get('default_event_id')
        if not event_id:
            return False
        event = self.env['sp_olympiad.event'].browse(event_id)
        return event.dates or False

    event_id = fields.Many2one(
        'sp_olympiad.event',
        string='Event',
        required=True,
        ondelete='cascade',
        index=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=_default_date,
    )
    sequence = fields.Integer(string='Sequence', default=10)
    label = fields.Char(
        string='Label',
        help='Short admin note for this day (e.g. Arrival, Registration Desk, City Tour).',
    )
