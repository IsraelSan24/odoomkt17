from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    requester_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Solicitante',
        ondelete='restrict',
        related='stock_move_id.requester_id'
    )
