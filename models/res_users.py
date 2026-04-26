import logging
from odoo import models
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_credentials(self, credential, env):
        auth_info = super()._check_credentials(credential, env)
        for user in self:
            if not user.active:
                raise AccessDenied()
            # Only check mentor verification for users who are actually mentors
            if user.has_group('sp_olympiad.group_sp_olympiad_mentor'):
                mentor = self.env['sp_olympiad.mentor'].sudo().search([
                    ('user_id', '=', user.id),
                ], limit=1)
                if mentor and not mentor.verified:
                    _logger.info("Blocked login for unverified mentor: %s", user.login)
                    raise AccessDenied()
        return auth_info
