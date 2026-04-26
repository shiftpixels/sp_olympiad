# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class OlympiadWebsite(http.Controller):

    @http.route(['/olympiad/categories'], type='http', auth="public", website=True, sitemap=True)
    def categories_list(self, **post):
        categories = request.env['sp_olympiad.category'].sudo().search([('active', '=', True)], order="sequence asc")
        return request.render("sp_olympiad.categories_page", {
            'categories': categories,
        })

    @http.route(['/olympiad/category/<model("sp_olympiad.category"):category>'], type='http', auth="public", website=True)
    def category_detail(self, category, **post):
        return request.render("sp_olympiad.category_detail_page", {
            'category': category,
        })

    @http.route(['/my/olympiad'], type='http', auth="user", website=True)
    def my_olympiad(self, **post):
        """Dashboard for verified mentors and administrators."""
        user = request.env.user
        if user.has_group('base.group_system'):
            return request.render("sp_olympiad.my_olympiad_dashboard", {})

        mentor = request.env['sp_olympiad.mentor'].search(
            [('user_id', '=', user.id)],
            limit=1
        )
        if not mentor or not mentor.verified or not user.active:
            return request.redirect('/web/login?redirect=/mentor/signup')

        return request.render("sp_olympiad.my_olympiad_dashboard", {})
