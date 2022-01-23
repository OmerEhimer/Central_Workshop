# -*- coding: utf-8 -*-
from odoo import http

# class CentralWorkshope(http.Controller):
#     @http.route('/central_workshope/central_workshope/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/central_workshope/central_workshope/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('central_workshope.listing', {
#             'root': '/central_workshope/central_workshope',
#             'objects': http.request.env['central_workshope.central_workshope'].search([]),
#         })

#     @http.route('/central_workshope/central_workshope/objects/<model("central_workshope.central_workshope"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('central_workshope.object', {
#             'object': obj
#         })