from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    request_count = fields.Integer(
        string="Solicitudes de Stock",
        compute="_compute_request_count",
        store=True
    )

    @api.depends("state")
    def _compute_request_count(self):
        for picking in self:
            picking.request_count = self.env["stock.request"].search_count(
                [("picking_id", "=", picking.id)]
            )

    def action_view_stock_requests(self):
        """Acción para abrir las solicitudes de stock relacionadas con la transferencia."""
        self.ensure_one()
        
        stock_requests = self.env["stock.request"].search([("picking_id", "=", self.id)])

        action = self.env.ref("mkt_supervision.stock_request_form_action").sudo().read()[0]

        if stock_requests:
            if len(stock_requests) == 1:
                action["res_id"] = stock_requests.id  # Abrir directamente si hay un solo registro
                action["views"] = [(self.env.ref("mkt_supervision.view_stock_request_form").id, "form")]
            else:
                action["domain"] = [("picking_id", "=", self.id)]  # Mostrar lista si hay varios registros
        else:
            action["context"] = {"default_picking_id": self.id}  # Mantener la opción de crear si no hay registros

        return action