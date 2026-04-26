# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import date
import uuid


class OlympiadCertificate(models.Model):
    _name = 'sp_olympiad.certificate'
    _description = 'Olympiad Certificate'
    _order = 'issue_date desc, id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Relations
    student_id = fields.Many2one(
        'sp_olympiad.student',
        string='Student',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Student who received this certificate'
    )
    project_id = fields.Many2one(
        'sp_olympiad.project',
        string='Project',
        required=True,
        ondelete='cascade',
        tracking=True,
        help='Project for which certificate was issued'
    )

    # Certificate Information
    certificate_type = fields.Selection([
        ('participation', 'Participation'),
        ('gold', 'Gold Medal'),
        ('silver', 'Silver Medal'),
        ('bronze', 'Bronze Medal'),
        ('honorable_mention', 'Honorable Mention'),
    ], string='Certificate Type', required=True, tracking=True, help='Type of certificate')

    # Event Information
    year = fields.Integer(
        string='Year',
        required=True,
        tracking=True,
        help='Year of the event'
    )
    issue_date = fields.Date(
        string='Issue Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Date when certificate was issued'
    )

    # Certificate Details
    certificate_number = fields.Char(
        string='Certificate Number',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        help='Unique certificate number'
    )

    # PDF
    pdf_file = fields.Binary(
        string='PDF File',
        help='Generated certificate PDF file'
    )
    pdf_filename = fields.Char(
        string='PDF Filename',
        help='Name of the PDF file'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate unique certificate number on creation."""
        for vals in vals_list:
            if not vals.get('certificate_number'):
                vals['certificate_number'] = self._generate_certificate_number(vals.get('year', date.today().year))
        return super().create(vals_list)

    def _generate_certificate_number(self, year):
        """Generate unique certificate number."""
        # Format: CERT-YYYY-XXXXX (where XXXX is random)
        random_part = str(uuid.uuid4()).upper()[:5]
        return f"CERT-{year}-{random_part}"

    @api.constrains('student_id', 'project_id', 'certificate_type')
    def _check_unique_certificate(self):
        """Prevent duplicate certificates for same student, project, and type."""
        for record in self:
            duplicates = self.search([
                ('student_id', '=', record.student_id.id),
                ('project_id', '=', record.project_id.id),
                ('certificate_type', '=', record.certificate_type),
                ('id', '!=', record.id),
            ], limit=1)
            if duplicates:
                raise ValidationError(
                    _(
                        'Certificate of type "%(type)s" already exists for student "%(student)s" in project "%(project)s".'
                    ) % {
                        'type': record.certificate_type,
                        'student': record.student_id.name,
                        'project': record.project_id.name,
                    }
                )

    @api.constrains('student_id', 'project_id')
    def _check_student_in_project(self):
        """Validate student is actually in the project."""
        for record in self:
            if record.student_id not in record.project_id.student_ids:
                raise ValidationError(
                    _(
                        'Student "%(student)s" is not in project "%(project)s".'
                    ) % {
                        'student': record.student_id.name,
                        'project': record.project_id.name,
                    }
                )

    @api.constrains('certificate_type', 'project_id')
    def _check_medal_certificate(self):
        """Validate medal certificates match project medal."""
        for record in self:
            if record.certificate_type != 'participation':
                if record.project_id.medal != record.certificate_type:
                    raise ValidationError(
                        _(
                            'Certificate type "%(cert_type)s" does not match project medal "%(medal)s".'
                        ) % {
                            'cert_type': record.certificate_type,
                            'medal': record.project_id.medal,
                        }
                    )

    def action_generate_pdf(self):
        """Generate PDF certificate."""
        self.ensure_one()
        # PDF generation will be implemented in the future
        # For now, just return a success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'PDF generation will be implemented in the future.',
                'type': 'info',
            }
        }

    def action_download_pdf(self):
        """Download PDF certificate."""
        self.ensure_one()
        if not self.pdf_file:
            raise ValidationError(_('No PDF file available for this certificate.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/sp_olympiad.certificate/{self.id}/pdf_file?download=true',
            'target': 'new',
        }
