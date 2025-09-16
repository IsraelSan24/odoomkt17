from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    requester_id = fields.Many2one(
        comodel_name='hr.employee',
        related='picking_id.requester_id'
    )

    def _prepare_common_svl_vals(self):
        res = super(StockMove, self)._prepare_common_svl_vals()
        res['requester_id'] = self.requester_id.id if self.requester_id else False
        return res
    