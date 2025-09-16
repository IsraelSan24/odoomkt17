from odoo import models, fields


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order.item"

    count_order = fields.Float(
        string="Productos Comprados", 
        related="line_id.purchased_qty",
        digits="Product Unit of Measure"
    )

    count_rfq = fields.Float(
        string="Productos Comprados", 
        related="line_id.product_qty",
        digits="Product Unit of Measure"
    )