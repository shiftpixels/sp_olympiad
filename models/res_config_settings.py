from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    olympiad_name = fields.Char(
        string="Competition Name",
        config_parameter='sp_olympiad.olympiad_name',
    )
    category_max_participants_limit = fields.Integer(
        string="Category Max Participants Limit",
        default=10,
        config_parameter='sp_olympiad.category_max_participants_limit',
    )
    mentor_signup_enabled = fields.Boolean(
        string='Enable Mentor Signup',
        config_parameter='sp_olympiad.mentor_signup_enabled',
    )
    mentor_verification_enabled = fields.Boolean(
        string='Require Email Verification',
        config_parameter='sp_olympiad.mentor_verification_enabled',
        default=True,
    )
    
    # Rate limiting settings
    login_rate_limit_window = fields.Integer(
        string='Login Rate Limit Window (seconds)',
        default=600,
        config_parameter='sp_olympiad.login_rate_limit_window',
        help='Time window in seconds for login rate limiting',
    )
    login_rate_limit_ip = fields.Integer(
        string='Login Rate Limit IP',
        default=30,
        config_parameter='sp_olympiad.login_rate_limit_ip',
        help='Maximum login attempts per IP within time window',
    )
    login_rate_limit_email = fields.Integer(
        string='Login Rate Limit Email',
        default=10,
        config_parameter='sp_olympiad.login_rate_limit_email',
        help='Maximum login attempts per email within time window',
    )
    signup_rate_limit_window = fields.Integer(
        string='Signup Rate Limit Window (seconds)',
        default=600,
        config_parameter='sp_olympiad.signup_rate_limit_window',
        help='Time window in seconds for signup rate limiting',
    )
    signup_rate_limit_ip = fields.Integer(
        string='Signup Rate Limit IP',
        default=12,
        config_parameter='sp_olympiad.signup_rate_limit_ip',
        help='Maximum signup attempts per IP within time window',
    )
    signup_rate_limit_email = fields.Integer(
        string='Signup Rate Limit Email',
        default=3,
        config_parameter='sp_olympiad.signup_rate_limit_email',
        help='Maximum signup attempts per email within time window',
    )
    resend_rate_limit_window = fields.Integer(
        string='Resend Rate Limit Window (seconds)',
        default=600,
        config_parameter='sp_olympiad.resend_rate_limit_window',
        help='Time window in seconds for resend verification rate limiting',
    )
    resend_rate_limit_ip = fields.Integer(
        string='Resend Rate Limit IP',
        default=20,
        config_parameter='sp_olympiad.resend_rate_limit_ip',
        help='Maximum resend attempts per IP within time window',
    )
    resend_rate_limit_email = fields.Integer(
        string='Resend Rate Limit Email',
        default=5,
        config_parameter='sp_olympiad.resend_rate_limit_email',
        help='Maximum resend attempts per email within time window',
    )

    @api.constrains('category_max_participants_limit')
    def _check_category_max_participants_limit(self):
        for record in self:
            if record.category_max_participants_limit < 1:
                raise ValidationError('Category Max Participants Limit must be at least 1.')

    def action_load_demo_data(self):
        """Load demo data for Olympiad module"""
        self.ensure_one()
        
        # Create categories
        demo_categories = [
            {'name': 'Environmental Science', 'code': 'ENV', 'max_participants': 3, 'sequence': 10},
            {'name': 'Biology', 'code': 'BIO', 'max_participants': 2, 'sequence': 20},
            {'name': 'Physics', 'code': 'PHY', 'max_participants': 3, 'sequence': 30},
            {'name': 'Mathematics', 'code': 'MAT', 'max_participants': 2, 'sequence': 40},
        ]
        
        category_ids = []
        for cat_data in demo_categories:
            category = self.env['sp_olympiad.category'].create({
                **cat_data,
                'active': True
            })
            category_ids.append(category.id)
        
        # Create event
        event = self.env['sp_olympiad.event'].create({
            'name': 'Innovate Germany 2027',
            'code_prefix': 'IG27-',
            'dates': '2027-06-15',
            'date_end': '2027-06-18',
            'state': 'draft',
            'category_ids': [(6, 0, category_ids)]
        })
        
        # Create mentor users and mentors
        mentor_group = self.env.ref('sp_olympiad.group_sp_olympiad_mentor')
        portal_group = self.env.ref('base.group_portal')
        
        demo_mentors = [
            {'name': 'Test Mentor 1', 'email': 'mentor1@test.com', 'country': 'base.de'},
            {'name': 'Test Mentor 2', 'email': 'mentor2@test.com', 'country': 'base.de'},
            {'name': 'Test Mentor 3', 'email': 'mentor3@test.com', 'country': 'base.tr'},
        ]
        
        for mentor_data in demo_mentors:
            email = mentor_data['email']
            user = self.env['res.users'].create({
                'name': mentor_data['name'],
                'login': email,
                'email': email,
                'password': 'Mentor123!',
                'active': True,
                'group_ids': [(6, 0, [portal_group.id, mentor_group.id])]
            })
            
            self.env['sp_olympiad.mentor'].create({
                'name': mentor_data['name'],
                'email': email,
                'user_id': user.id,
                'country_id': self.env.ref(mentor_data['country']).id,
                'verified': True
            })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Demo data loaded successfully!',
                'type': 'success',
            }
        }

    def action_clear_demo_data(self):
        """Clear demo data for Olympiad module"""
        self.ensure_one()
        
        # Clear demo mentors (created by demo data)
        demo_mentor_emails = ['mentor1@test.com', 'mentor2@test.com', 'mentor3@test.com']
        mentors = self.env['sp_olympiad.mentor'].search([('email', 'in', demo_mentor_emails)])
        
        # Get user IDs before deleting mentors
        user_ids = mentors.mapped('user_id').ids
        
        # Delete mentors
        mentors.unlink()
        
        # Delete mentor users
        if user_ids:
            self.env['res.users'].browse(user_ids).unlink()
        
        # Clear demo events
        demo_events = self.env['sp_olympiad.event'].search([('code_prefix', '=', 'IG27-')])
        demo_events.unlink()
        
        # Clear demo categories
        demo_category_codes = ['ENV', 'BIO', 'PHY', 'MAT']
        demo_categories = self.env['sp_olympiad.category'].search([('code', 'in', demo_category_codes)])
        demo_categories.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Demo data cleared successfully!',
                'type': 'success',
            }
        }
