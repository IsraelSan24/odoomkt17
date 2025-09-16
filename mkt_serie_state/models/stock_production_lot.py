from odoo import _, api, fields, models


class ProductionLor(models.Model):
    _inherit = 'stock.production.lot'

    usage_status = fields.Selection(selection=[
            ('new', 'New'),
            ('used', 'Used'),
        ], required=True, default='new', string='Status')