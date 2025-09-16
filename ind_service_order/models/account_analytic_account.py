from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    model = fields.Char(string='Modelo')
    serie = fields.Char(string='N° de Serie')
    brand = fields.Char(string='Marca')
    hour_meter = fields.Float(string='Horómetro')
