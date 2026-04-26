# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class OlympiadStudent(models.Model):
    _name = 'sp_olympiad.student'
    _description = 'Olympiad Student'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Personal Information
    first_name = fields.Char(
        string='First Name',
        required=True,
        tracking=True,
        help='Student\'s first name'
    )
    last_name = fields.Char(
        string='Last Name',
        required=True,
        tracking=True,
        help='Student\'s last name'
    )
    name = fields.Char(
        string='Full Name',
        compute='_compute_name',
        store=True,
        readonly=True,
        help='Full name (first name + last name)'
    )
    birth_date = fields.Date(
        string='Birth Date',
        required=True,
        tracking=True,
        help='Student\'s date of birth'
    )
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True,
        readonly=True,
        help='Student\'s age at event date'
    )
    gender = fields.Selection(
        [
            ('M', 'Male'),
            ('F', 'Female'),
            ('D', 'Diverse'),
        ],
        string='Gender',
        required=True,
        tracking=True,
        help='Student\'s gender'
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        required=True,
        tracking=True,
        help='Student\'s country of residence'
    )

    # Contact Information
    email = fields.Char(
        string='Email',
        help='Student\'s email address for communication'
    )
    phone = fields.Char(
        string='Phone',
        help='Student\'s phone number for emergencies'
    )

    # Dietary Information
    allergies = fields.Text(
        string='Allergies',
        help='Any food allergies or dietary restrictions'
    )
    dietary_restrictions = fields.Text(
        string='Dietary Restrictions',
        help='Specific dietary requirements (e.g., vegetarian, gluten-free)'
    )

    # Logistics
    visa_required = fields.Boolean(
        string='Visa Required',
        default=False,
        tracking=True,
        help='Whether the student requires a visa for travel'
    )
    tshirt_size = fields.Selection(
        [
            ('XS', 'Extra Small'),
            ('S', 'Small'),
            ('M', 'Medium'),
            ('L', 'Large'),
            ('XL', 'Extra Large'),
            ('XXL', 'Double Extra Large'),
        ],
        string='T-Shirt Size',
        required=True,
        tracking=True,
        help='Student\'s t-shirt size for event merchandise'
    )

    # Accommodation
    accommodation_ids = fields.Many2many(
        'sp_olympiad.event.accommodation',
        'student_accommodation_rel',
        'student_id',
        'accommodation_id',
        string='Accommodation Nights',
        help='Selected accommodation nights from event options'
    )
    no_accommodation = fields.Boolean(
        string='No Accommodation',
        default=False,
        help='If checked, accommodation selection is ignored'
    )
    accommodation_nights = fields.Integer(
        string='Number of Nights',
        compute='_compute_accommodation_nights',
        store=True,
        readonly=True,
        help='Total number of accommodation nights selected'
    )

    # Relations
    project_id = fields.Many2one(
        'sp_olympiad.project',
        string='Project',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Project this student belongs to'
    )

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        """Compute full name from first and last name."""
        for record in self:
            if record.first_name and record.last_name:
                record.name = f"{record.first_name} {record.last_name}"
            else:
                record.name = record.first_name or record.last_name or ''

    @api.depends('birth_date', 'project_id.dates')
    def _compute_age(self):
        """Compute student's age at event date."""
        for record in self:
            if record.birth_date and record.project_id and record.project_id.dates:
                today = date.today()
                event_date = record.project_id.dates
                
                # Calculate age at event date
                age = event_date.year - record.birth_date.year - (
                    (event_date.month, event_date.day) < (record.birth_date.month, record.birth_date.day)
                )
                record.age = max(age, 0)
            else:
                record.age = 0

    @api.depends('accommodation_ids', 'no_accommodation')
    def _compute_accommodation_nights(self):
        """Compute total number of accommodation nights."""
        for record in self:
            if record.no_accommodation:
                record.accommodation_nights = 0
            else:
                record.accommodation_nights = len(record.accommodation_ids)

    @api.constrains('birth_date')
    def _check_birth_date(self):
        """Validate birth date is not in the future."""
        for record in self:
            if record.birth_date and record.birth_date > date.today():
                raise ValidationError(_('Birth date cannot be in the future.'))

    @api.constrains('age', 'project_id')
    def _check_age_range(self):
        """Validate student age is within event's age boundaries."""
        for record in self:
            if not record.project_id or not record.project_id.dates:
                continue
            
            event = record.project_id
            if not event.age_junior_min or not event.age_junior_max:
                continue
            if not event.age_senior_min or not event.age_senior_max:
                continue
            
            # Check if age is within valid range
            if record.age < event.age_junior_min or record.age > event.age_senior_max:
                raise ValidationError(
                    _(
                        'Student age (%(age)d) must be between %(min_age)d and %(max_age)d years old.'
                    ) % {
                        'age': record.age,
                        'min_age': event.age_junior_min,
                        'max_age': event.age_senior_max,
                    }
                )

    @api.constrains('accommodation_ids', 'no_accommodation', 'project_id')
    def _check_accommodation_dates(self):
        """Validate accommodation dates are within event date range."""
        for record in self:
            if record.no_accommodation or not record.project_id:
                continue
            
            event = record.project_id
            if not event.dates or not event.date_end:
                continue
            
            for accommodation in record.accommodation_ids:
                if accommodation.date < event.dates or accommodation.date > event.date_end:
                    raise ValidationError(
                        _(
                            'Accommodation date (%(date)s) must be within event date range '
                            '(%(start)s to %(end)s).'
                        ) % {
                            'date': accommodation.date,
                            'start': event.dates,
                            'end': event.date_end,
                        }
                    )

    @api.constrains('no_accommodation', 'accommodation_ids')
    def _check_accommodation_consistency(self):
        """Validate accommodation consistency."""
        for record in self:
            if record.no_accommodation and record.accommodation_ids:
                raise ValidationError(
                    _('Cannot select accommodation nights when "No Accommodation" is checked.')
                )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_in_active_project(self):
        """Prevent deletion of students in active projects."""
        for record in self:
            if record.project_id and record.project_id.state in ['draft', 'open', 'submitted', 'paid']:
                raise ValidationError(
                    _(
                        'Cannot delete student "%(name)s" because the project "%(project)s" is in %(state)s state. '
                        'Archive the project or change its state first.'
                    ) % {
                        'name': record.name,
                        'project': record.project_id.name,
                        'state': record.project_id.state,
                    }
                )
