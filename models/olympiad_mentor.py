from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OlympiadMentor(models.Model):
    _name = 'sp_olympiad.mentor'
    _description = 'Olympiad Mentor'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, translate=True)
    email = fields.Char(string='Email', required=True)
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        required=True,
        help='Country of residence'
    )
    branch = fields.Char(
        string='Branch/Field',
        help='Subject area (e.g. Physics, Mathematics, Biology)'
    )
    phone = fields.Char(string='Phone')
    whatsapp = fields.Char(
        string='WhatsApp',
        help='WhatsApp contact number'
    )
    verified = fields.Boolean(
        string='Email Verified',
        default=False,
        readonly=True,
        help='Set to True after email verification.'
    )
    # System fields
    user_id = fields.Many2one(
        'res.users',
        string='Related User',
        readonly=True,
        ondelete='restrict',
        help='Odoo user account for this mentor'
    )
    verification_token = fields.Char(
        string='Verification Token',
        readonly=True,
        help='Token for email verification'
    )
    token_expiry = fields.Datetime(
        string='Token Expiry',
        readonly=True,
        help='Verification token expires at this time'
    )
    created_date = fields.Datetime(
        string='Created',
        default=fields.Datetime.now,
        readonly=True
    )

    # Compute field for display
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('name', 'email')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.email})"

    @api.constrains('email')
    def _check_unique_email(self):
        for record in self:
            if record.email:
                existing = self.search(
                    [('email', '=', record.email), ('id', '!=', record.id)],
                    limit=1
                )
                if existing:
                    raise ValidationError(
                        _('Email %s is already registered by another mentor.') %
                        record.email
                    )

    @api.constrains('country_id')
    def _check_allowed_countries(self):
        """Ensure only specific countries can register (Layer 3)."""
        allowed_codes = ['TR', 'DE']
        for record in self:
            if record.country_id and record.country_id.code not in allowed_codes:
                raise ValidationError(
                    _("Registration is currently only available for mentors from: %s") % ", ".join(allowed_codes)
                )

    @api.constrains('user_id')
    def _check_unique_user(self):
        for record in self:
            if record.user_id:
                existing = self.search(
                    [('user_id', '=', record.user_id.id), ('id', '!=', record.id)],
                    limit=1
                )
                if existing:
                    raise ValidationError(
                        _('User %s is already linked to another mentor record.') %
                        record.user_id.name
                    )

    def generate_verification_token(self):
        """Generate a new verification token valid for 24 hours."""
        import uuid
        from datetime import datetime, timedelta

        for record in self:
            record.verification_token = str(uuid.uuid4())
            record.token_expiry = datetime.now() + timedelta(hours=24)

    def send_verification_email(self):
        """Send verification email with token link."""
        self.ensure_one()
        if not self.email:
            raise ValidationError(_('Cannot send email: No email address.'))

        # Generate token if not exists
        if not self.verification_token or self.verification_token_expired():
            self.generate_verification_token()

        # Email template
        template = self.env.ref(
            'sp_olympiad.mentor_verification_email_template',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(
                self.id,
                force_send=True,
                raise_exception=False
            )
        return True

    def verification_token_expired(self):
        """Check if current token is expired."""
        self.ensure_one()
        if not self.token_expiry:
            return True
        from datetime import datetime
        return datetime.now() > self.token_expiry

    def verify_email(self, token):
        """Verify email with token. Returns True if successful."""
        self.ensure_one()
        if not token or not self.verification_token:
            return False

        if token != self.verification_token:
            return False

        if self.verification_token_expired():
            return False

        values = {
            'verified': True,
            'verification_token': False,
            'token_expiry': False,
        }
        self.write(values)

        # Activate linked user and grant mentor role only after email verification.
        if self.user_id:
            # Write all values in a single call to prevent Odoo from resetting active=False
            user_values = {'active': True}
            mentor_group = self.env.ref('sp_olympiad.group_sp_olympiad_mentor', raise_if_not_found=False)
            if mentor_group and mentor_group not in self.user_id.group_ids:
                user_values['group_ids'] = [(4, mentor_group.id)]
            # Force active=True in write to prevent Odoo from auto-enabling it on group change
            self.user_id.sudo().write(user_values)
            # Extra safety: ensure active is True after write
            if not self.user_id.active:
                self.user_id.sudo().write({'active': True})

        return True

    def action_resend_verification_email(self):
        """Resend verification email."""
        self.ensure_one()
        if self.verified:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Email Already Verified'),
                    'message': _('This mentor has already verified their email.'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        self.send_verification_email()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Verification Email Sent'),
                'message': _('A new verification email has been sent.'),
                'type': 'success',
                'sticky': False,
            }
        }
