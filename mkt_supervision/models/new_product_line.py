from odoo import models, fields, api, _

class NewProductLine(models.Model):
    _name = "new.product.line"
    _description = "Línea de Productos Nuevos"

    new_product = fields.Char(string="Producto", required=True)
    new_description = fields.Char(string="Descripción")
    new_qty = fields.Float(string="Cantidad", required=True, default=1.0)
    new_uom = fields.Many2one("uom.uom", string="Unidad de Medida", required=True, default=lambda self: self._default_uom())
    date_required = fields.Datetime(
        related="request_id.date_required",
        string="Fecha de Transferencia",
        required=True,
        tracking=True,
    )
    request_id = fields.Many2one(
        comodel_name="stock.request",
        string="Solicitud de Stock",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )

    @api.model
    def _default_uom(self):
        return self.env.ref("uom.product_uom_unit").id