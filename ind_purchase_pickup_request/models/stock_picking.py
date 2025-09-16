from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        res = super(StockPicking, self).action_done()
        # Actualizar las solicitudes de recojo relacionadas después de confirmar el picking
        for picking in self:
            related_requests = self.env['pickup.request'].search([
                ('purchase_order_id', '=', picking.purchase_id.id)
            ])
            if related_requests:
                related_requests._compute_picking_ids()
                related_requests._compute_picking_info()
        return res
