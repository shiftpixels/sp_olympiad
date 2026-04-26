# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OlympiadProject(models.Model):
    _name = 'sp_olympiad.project'
    _description = 'Olympiad Project'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Project Name',
        required=True,
        tracking=True,
        help='Name of the project'
    )
    code = fields.Char(
        string='Project Code',
        compute='_compute_code',
        store=True,
        readonly=True,
        help='Unique project code (auto-generated)'
    )
    year = fields.Integer(
        string='Year',
        related='event_id.year',
        store=True,
        readonly=True,
        help='Event year'
    )
    mentor_id = fields.Many2one(
        'res.users',
        string='Mentor',
        required=True,
        tracking=True,
        help='Mentor responsible for this project'
    )
    category_id = fields.Many2one(
        'sp_olympiad.category',
        string='Category',
        required=True,
        tracking=True,
        help='Project category'
    )
    pres_lang = fields.Selection(
        [
            ('en', 'English'),
            ('de', 'German'),
        ],
        string='Presentation Language',
        required=True,
        default='en',
        tracking=True,
        help='Language for project presentation'
    )
    mentor_excursion = fields.Boolean(
        string='Mentor Excursion',
        default=False,
        tracking=True,
        help='Whether mentor participates in excursion'
    )

    # Files
    abstract_file = fields.Binary(
        string='Abstract File',
        help='Project abstract document'
    )
    abstract_filename = fields.Char(
        string='Abstract Filename',
        help='Name of the abstract file'
    )
    research_paper = fields.Binary(
        string='Research Paper',
        help='Research paper document'
    )
    research_paper_filename = fields.Char(
        string='Research Paper Filename',
        help='Name of the research paper file'
    )

    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, help='Project status')
    paid = fields.Boolean(
        string='Paid',
        default=False,
        tracking=True,
        help='Whether payment has been completed'
    )

    # Payment
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
        readonly=True,
        help='Total cost including registration, accommodation, and excursion'
    )
    # payment_tx_id = fields.Many2one(
    #     'payment.transaction',
    #     string='Payment Transaction',
    #     readonly=True,
    #     help='Payment transaction linked to this project'
    # )

    # Students
    num_students = fields.Integer(
        string='Number of Students',
        compute='_compute_num_students',
        store=True,
        readonly=True,
        help='Total number of students in the project'
    )
    student_ids = fields.Many2many(
        'sp_olympiad.student',
        'student_project_rel',
        'project_id',
        'student_id',
        string='Students',
        help='Students participating in this project'
    )

    # Event
    event_id = fields.Many2one(
        'sp_olympiad.event',
        string='Event',
        required=True,
        tracking=True,
        ondelete='restrict',
        help='Event this project belongs to'
    )

    # Evaluation
    project_score = fields.Float(
        string='Project Score',
        compute='_compute_project_score',
        store=True,
        readonly=True,
        help='Average score from jury evaluations'
    )
    medal = fields.Selection([
        ('participation', 'Participation'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
        ('honorable_mention', 'Honorable Mention'),
    ], string='Medal', compute='_compute_medal', store=True, readonly=True, help='Medal awarded to project')

    # Age Group
    age_group = fields.Selection([
        ('junior', 'Junior'),
        ('senior', 'Senior'),
    ], string='Age Group', compute='_compute_age_group', store=True, readonly=True, help='Age group based on oldest student')

    @api.depends('event_id.code_prefix', 'event_id.year', 'category_id.code')
    def _compute_code(self):
        """Compute project code."""
        for record in self:
            if record.event_id and record.category_id:
                # Get sequence number for this event and category
                sequence = self._get_sequence_number(record.event_id.id, record.category_id.id)
                record.code = f"{record.event_id.code_prefix}{record.event_id.year}-{record.category_id.code}-{sequence:03d}"
            else:
                record.code = ''

    def _get_sequence_number(self, event_id, category_id):
        """Get next sequence number for event and category."""
        # Count existing projects for this event and category
        count = self.search_count([
            ('event_id', '=', event_id),
            ('category_id', '=', category_id),
            ('id', '!=', self.id or 0),
        ])
        return count + 1

    @api.depends('student_ids', 'student_ids.accommodation_nights', 'student_ids.excursion', 'event_id', 'mentor_excursion')
    def _compute_total_amount(self):
        """Compute total amount for the project."""
        for record in self:
            if not record.event_id:
                record.total_amount = 0.0
                continue
            
            event = record.event_id
            total = event.registration_fee or 0.0
            
            # Add accommodation fees
            for student in record.student_ids:
                if not student.no_accommodation:
                    nights = student.accommodation_nights or 0
                    total += nights * (event.accommodation_fee or 0.0)
                
                # Add excursion fee if student participates
                if student.excursion:
                    total += event.excursion_fee or 0.0
            
            # Add mentor excursion fee
            if record.mentor_excursion:
                total += event.excursion_fee or 0.0
            
            record.total_amount = total

    @api.depends('student_ids')
    def _compute_num_students(self):
        """Compute number of students."""
        for record in self:
            record.num_students = len(record.student_ids)

    @api.depends('student_ids.age')
    def _compute_age_group(self):
        """Compute age group based on oldest student."""
        for record in self:
            if not record.student_ids or not record.event_id:
                record.age_group = False
                continue
            
            event = record.event_id
            max_age = max(record.student_ids.mapped('age')) if record.student_ids else 0
            
            if not event.age_junior_min or not event.age_junior_max:
                record.age_group = False
                continue
            if not event.age_senior_min or not event.age_senior_max:
                record.age_group = False
                continue
            
            if event.age_junior_min <= max_age <= event.age_junior_max:
                record.age_group = 'junior'
            elif event.age_senior_min <= max_age <= event.age_senior_max:
                record.age_group = 'senior'
            else:
                record.age_group = False

    @api.depends('student_ids', 'student_ids.age')
    def _compute_project_score(self):
        """Compute average project score from jury evaluations."""
        for record in self:
            # This will be computed from jury scores in the future
            # For now, set to 0
            record.project_score = 0.0

    @api.depends('project_score', 'event_id')
    def _compute_medal(self):
        """Compute medal based on project score."""
        for record in self:
            if not record.event_id:
                record.medal = 'participation'
                continue
            
            event = record.event_id
            score = record.project_score
            
            if score >= (event.medal_gold_min or 91):
                record.medal = 'gold'
            elif score >= (event.medal_silver_min or 81):
                record.medal = 'silver'
            elif score >= (event.medal_bronze_min or 65):
                record.medal = 'bronze'
            elif score >= (event.medal_hm_min or 50):
                record.medal = 'honorable_mention'
            else:
                record.medal = 'participation'

    @api.constrains('num_students', 'category_id')
    def _check_max_participants(self):
        """Validate number of students does not exceed category limit."""
        for record in self:
            if record.category_id and record.num_students > record.category_id.max_participants:
                raise ValidationError(
                    _(
                        'Number of students (%(num)d) cannot exceed category maximum (%(max)d).'
                    ) % {
                        'num': record.num_students,
                        'max': record.category_id.max_participants,
                    }
                )

    @api.constrains('num_students', 'category_id')
    def _check_solo_category(self):
        """Validate solo categories have exactly one student."""
        for record in self:
            if record.category_id and record.category_id.is_solo and record.num_students != 1:
                raise ValidationError(
                    _(
                        'Solo category "%(category)s" requires exactly one student, but %(num)d students are added.'
                    ) % {
                        'category': record.category_id.name,
                        'num': record.num_students,
                    }
                )

    @api.constrains('state', 'abstract_file')
    def _check_abstract_required(self):
        """Validate abstract file is required for published projects."""
        for record in self:
            if record.state == 'published' and not record.abstract_file:
                raise ValidationError(
                    _('Abstract file is required to publish a project.')
                )

    @api.constrains('state', 'paid')
    def _check_payment_required(self):
        """Validate payment is required for paid state."""
        for record in self:
            if record.state == 'paid' and not record.paid:
                raise ValidationError(
                    _('Payment must be completed to mark project as paid.')
                )

    @api.constrains('research_paper', 'event_id')
    def _check_research_paper_deadline(self):
        """Validate research paper submission before deadline."""
        for record in self:
            if record.research_paper and record.event_id and record.event_id.research_paper_deadline:
                # This is a soft validation - admin can override
                # Just log a warning for now
                pass

    @api.ondelete(at_uninstall=False)
    def _unlink_except_published(self):
        """Prevent deletion of published projects."""
        for record in self:
            if record.state == 'published':
                raise ValidationError(
                    _(
                        'Cannot delete published project "%(name)s". Archive it instead.'
                    ) % {
                        'name': record.name,
                    }
                )

    def action_publish(self):
        """Publish project."""
        self.write({'state': 'published'})
        return True

    def action_finish(self):
        """Finish project."""
        self.write({'state': 'finished'})
        return True

    def action_cancel(self):
        """Cancel project."""
        self.write({'state': 'cancelled'})
        return True
