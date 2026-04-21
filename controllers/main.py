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
