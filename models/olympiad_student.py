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
    excursion = fields.Boolean(
        string='Excursion',
        default=False,
        tracking=True,
        help='Whether the student participates in excursion'
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
    mentor_id = fields.Many2one(
        'res.users',
        string='Mentor',
        required=True,
        tracking=True,
        help='Mentor who manages this student'
    )
    project_ids = fields.Many2many(
        'sp_olympiad.project',
        'student_project_rel',
        'student_id',
        'project_id',
        string='Projects',
        help='Projects this student has participated in'
    )

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        """Compute full name from first and last name."""
        for record in self:
            if record.first_name and record.last_name:
                record.name = f"{record.first_name} {record.last_name}"
            else:
                record.name = record.first_name or record.last_name or ''

    @api.depends('birth_date')
    def _compute_age(self):
        """Compute student's age at current date."""
        for record in self:
            if record.birth_date:
                today = date.today()
                age = today.year - record.birth_date.year - (
                    (today.month, today.day) < (record.birth_date.month, record.birth_date.day)
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

    @api.constrains('age')
    def _check_age_range(self):
        """Validate student age is within reasonable range."""
        for record in self:
            if record.age < 5 or record.age > 25:
                raise ValidationError(
                    _(
                        'Student age (%(age)d) must be between 5 and 25 years old.'
                    ) % {
                        'age': record.age,
                    }
                )

    @api.constrains('accommodation_ids', 'no_accommodation')
    def _check_accommodation_consistency(self):
        """Validate accommodation consistency."""
        for record in self:
            if record.no_accommodation and record.accommodation_ids:
                raise ValidationError(
                    _('Cannot select accommodation nights when "No Accommodation" is checked.')
                )

    @api.constrains('mentor_id')
    def _check_mentor_group(self):
        """Validate mentor belongs to Olympiad Mentor group."""
        for record in self:
            if record.mentor_id:
                mentor_group = self.env.ref('sp_olympiad.group_sp_olympiad_mentor', raise_if_not_found=False)
                admin_group = self.env.ref('sp_olympiad.group_sp_olympiad_admin', raise_if_not_found=False)
                if mentor_group and admin_group:
                    if not (record.mentor_id.has_group('sp_olympiad.group_sp_olympiad_mentor') or
                            record.mentor_id.has_group('sp_olympiad.group_sp_olympiad_admin')):
                        raise ValidationError(
                            _(
                                'Mentor "%(mentor)s" must belong to Olympiad Mentor or Admin group.'
                            ) % {
                                'mentor': record.mentor_id.name,
                            }
                        )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_in_active_projects(self):
        """Prevent deletion of students in active projects."""
        for record in self:
            # Check if student is in any active projects
            active_projects = record.project_ids.filtered(
                lambda p: p.state in ['draft', 'published']
            )
            if active_projects:
                project_names = ', '.join(active_projects.mapped('name'))
                raise ValidationError(
                    _(
                        'Cannot delete student "%(name)s" because they are in active projects: %(projects)s. '
                        'Archive the projects or change their state first.'
                    ) % {
                        'name': record.name,
                        'projects': project_names,
                    }
                )
