from odoo import _, api, fields, models, exceptions
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

_STATES = [
    ("draft", "Borrador"),
    ("to_approve", "Por Aprobar"),
    ("approved", "Aprobado"),
    ("rejected", "Rechazado"),
    ("done", "Hecho"),
]


class StockRequestLine(models.Model):

    _name = "stock.request.line"
    _description = "Línea de Solicitud de Stock"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Descripción", tracking=True)

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UdM",
        tracking=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id"
    )    

    product_qty = fields.Float(
        string="Cantidad", 
        tracking=True, 
        digits="Unidad de Medida del Producto"
    )
    
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Compañía",
        store=True,
    )
    
    cancelled = fields.Boolean(readonly=True, default=False, copy=False)
    
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Centro de Costo",
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Solicitado por",
        store=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Asignado a",
        store=True,
    )
    request_id = fields.Many2one(
        comodel_name="stock.request",
        string="Solicitud de Stock",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    date_start = fields.Date(
        related="request_id.date_start",
        store=True,
    )
    description = fields.Text(
        related="request_id.description",
        string="Descripción de RS",
        store=True,
        readonly=False,
    )
    origin = fields.Char(
        related="request_id.origin", 
        string="Documento de Origen", 
        store=True
    )
    date_required = fields.Datetime(
        related="request_id.date_required",
        string="Fecha de Transferencia",
        required=True,
        tracking=True,
    )
    is_editable = fields.Boolean(
        compute="_compute_is_editable",
        readonly=True
    )
    specifications = fields.Text()
    request_state = fields.Selection(
        string="Estado de Solicitud",
        related="request_id.state",
        store=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[],
        required=True,
    )

    @api.depends(
        "product_id",
        "name",
        "product_uom_id",
        "product_qty",
        "analytic_account_id",
        "date_required",
        "specifications",
        # "purchase_lines",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        """ for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False """
            
    def do_cancel(self):
        """Actions to perform when cancelling a stock request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a stock request line."""
        self.write({"cancelled": False})

    def write(self, vals):
        res = super(StockRequestLine, self).write(vals)
        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res
    
    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        """ if self.mapped("purchase_lines"):
            raise UserError(
                _("No puedes eliminar un registro que hace referencia a lineas de solicitud")
            ) """
        for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "Puedes eliminar una línea de solicitud "
                        "si la solicitud de stock está en estado borrador"
                    )
                )
        return super(StockRequestLine, self).unlink()
    
    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(self.product_id.code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name

    @api.onchange('company_id') 
    def _onchange_company_id(self):
        # Aplicar un dominio al campo account_analytic_id basado en la compañía seleccionada
        domain = [('company_id', '=', self.company_id.id)]
        return {'domain': {'analytic_account_id': domain}} 
            
    @api.onchange("request_id", "product_id")
    def _onchange_product_id_domain(self):
        for line in self:
            domain = []
            
            if line.request_id:
                if line.request_id.picking_type_code == "outgoing" and line.request_id.location_id:
                    stock_quants = self.env["stock.quant"].search([
                        ("location_id", "=", line.request_id.location_id.id),
                        ("quantity", ">", 0)
                    ])
                    domain = [("id", "in", stock_quants.mapped("product_id").ids)]
                else:
                    domain = [("purchase_ok", "=", True)]

            return {"domain": {"product_id": domain}}