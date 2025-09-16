from odoo import fields, models, api, _
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Borrador"),
    ("to_approve", "Por aprobar"),
    ("sent", "Enviado"),
    ("rejected", "Rechazado"),
    ("done", "Hecho"),
]

class StockRequest(models.Model):
    _name = 'stock.request'
    _description = 'Solicitud de Stock'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("stock.request") or _("New")
    
    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
                
    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [('code', 'in', ['incoming', 'outgoing']), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [('code', 'in', ['incoming', 'outgoing']), ("warehouse_id", "=", False)]
            )
        return types[:1]
    
    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    requested_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        tracking=True,
        default=_get_default_requested_by,
        index=True,
    )
    
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Asignado a",
        tracking=True,
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("mkt_supervision.group_stock_request_manager").id,
            )
        ],
        index=True,
    )
    
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Tipo de Operación",
        required=True,
        default=_default_picking_type,
        domain="[('code', 'in', ['incoming', 'outgoing'])]",
    )

    picking_type_code = fields.Selection(
        related="picking_type_id.code", 
        store=True
    )
    
    movement_type = fields.Selection(
        [('customer', 'Cliente'), ('employee', 'Empleado'), ('supplier', 'Proveedor')],
        string="Tipo de Contacto",
        required=True
    )

    partner_id = fields.Many2one(
        'res.partner', string="Recibir de / Entregar a"
    )
    
    line_ids = fields.One2many(
        comodel_name="stock.request.line",
        inverse_name="request_id",
        string="Productos",
        readonly=False,
        copy=True,
        tracking=True,
    )
    
    is_name_editable = fields.Boolean(
        default=lambda self: self.env.user.has_group("base.group_no_one"),
    )
    
    origin = fields.Char(string="Documento de Origen")
    
    description = fields.Text(string="Descripción")
    
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        default=_company_get,
        tracking=True,
    )
    
    date_start = fields.Date(
        string="Fecha de Creación",
        help="Fecha cuando el usuario inicia la solicitud.",
        default=fields.Date.context_today,
        tracking=True,
    )
    
    state = fields.Selection(
        selection=_STATES,
        string="Estado",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
        compute="_compute_state_from_picking",
        inverse="_inverse_state",  # 🔥 Permite edición manual
        store=True,  # 🔥 Guarda en la BD
    )
    
    date_required = fields.Datetime(
        string="Fecha de Transferencia",
        help="Fecha prevista de Despacho",
        default=fields.Datetime.now,
        tracking=True,
    )
    
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    
    line_count = fields.Integer(
        string="Cantidad de líneas de despacho",
        compute="_compute_line_count",
        readonly=True,
    )
    
    picking_count = fields.Integer(
        string="Cantidad de salidas asociadas",
        compute="_compute_picking_count",
        readonly=True,
    )

    location_id = fields.Many2one(
        'stock.location',
        string="Ubicación Origen",
        domain=lambda self: [('usage', '=', 'internal'), ('id', 'in', self.env.user.stock_location_ids.ids)],
        default=lambda self: self.picking_type_id.default_location_src_id,
    )

    location_dest_id = fields.Many2one(
        'stock.location',
        string="Ubicación Destino",
        domain=lambda self: [('usage', '=', 'internal'), ('id', 'in', self.env.user.stock_location_ids.ids)],
        default=lambda self: self.picking_type_id.default_location_dest_id,
    )
    
    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True)

    new_product_ids = fields.One2many("new.product.line", "request_id", string="Productos Nuevos", readonly=False, copy=True, tracking=True)
    

    @api.onchange('picking_type_id', 'movement_type')
    def _onchange_picking_type(self):
        """Cambia location_id o location_dest_id según el tipo de operación y movimiento"""
        if self.picking_type_code == 'incoming':
            self.location_id = 4 if self.movement_type == 'supplier' else 5
        elif self.picking_type_code == 'outgoing':
            self.location_dest_id = 4 if self.movement_type == 'supplier' else 5
    
    def write(self, vals):
        res = super(StockRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res
    
    def copy(self, default=None):
        default = dict(default or {})
        default["name"] = self.env["ir.sequence"].next_by_code("stock.request") or _("New")
        default["state"] = "draft"
        return super(StockRequest, self).copy(default)
    
    def check_auto_reject(self):
        """When all lines are cancelled the stock request should be
        auto-rejected."""
        for mr in self:
            if not mr.line_ids.filtered(lambda l: l.cancelled is False):
                mr.write({"state": "rejected"})
    
    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))
    
    @api.depends("line_ids")
    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count= len(rec.mapped("picking_id"))
    
    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id
    
    @api.model
    def create(self, vals):
        if not vals.get("name") or vals["name"] in ["New", _("New")]:
            vals["name"] = self.env["ir.sequence"].next_by_code("stock.request") or _("New")

        request = super(StockRequest, self).create(vals)

        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])

        return request
    
    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"
    
    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("No puedes borrar una solicitud de stock que no está en borrador")
                )
        return super(StockRequest, self).unlink()
    
    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled", "new_product_ids.new_qty")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and (
                any(not line.cancelled and line.product_qty for line in rec.line_ids) or
                any(new_product.new_qty for new_product in rec.new_product_ids)
            )
            
    def action_view_stock_request_line(self):
        action = (
            self.env.ref("mkt_supervision.stock_request_line_form_action")
            .sudo()
            .read()[0]
        )
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("mkt_supervision.stock_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action
    
    def action_view_stock_picking(self):
        action = (
            self.env.ref("stock.action_picking_tree_all")
            .sudo()
            .read()[0]
        )
        pickings = self.mapped("picking_id")
        if len(pickings) > 1:
            action["domain"] = [("id", "in", pickings.ids)]
        elif pickings:
            action["views"] = [
                (self.env.ref("stock.view_picking_form").id, "form")
            ]
            action["res_id"] = pickings.ids[0]
        return action
    
    @api.depends("picking_id.state", "picking_id", "state", "picking_id.date_done")
    def _compute_state_from_picking(self):
        for request in self:
            if request.picking_id:  # Asegurar que hay un picking
                if request.picking_id.state == 'done':
                    request.state = 'done'
                elif request.picking_id.state == 'cancel':  # Mejor sin lista innecesaria
                    request.state = 'rejected'
                else:
                    request.state = 'draft'

    def _inverse_state(self):
        """Este método permite que el campo state se edite manualmente sin que el cálculo lo sobreescriba."""
        pass

    @api.constrains('picking_id')
    def _check_picking_state(self):
        """Verifica cambios en picking_id y actualiza el estado del request."""
        for request in self:
            if request.picking_id:
                request._compute_state_from_picking()
            
    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_to_approve(self):
        self.to_approve_allowed_check()
        return self.write({"state": "to_approve"})

    def button_approved(self):
        self.create_stock_picking()
        return self.write({"state": "sent"})

    def button_rejected(self):
        self.mapped("line_ids").do_cancel()
        return self.write({"state": "rejected"})

    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _(
                        "No puedes obtener una aprobación para una solicitud de stock "
                        "que está vacía. (%s)"
                    )
                    % rec.name
                )

    def create_stock_picking(self):
        for request in self:
            picking_vals = {
                'partner_id': request.partner_id.id,
                'location_id': request.location_id.id if request.location_id else request.picking_type_id.default_location_src_id.id,
                'location_dest_id': request.location_dest_id.id if request.location_dest_id else request.picking_type_id.default_location_dest_id.id,
                'picking_type_id': request.picking_type_id.id,
                'origin': request.name,
                'scheduled_date': request.date_required,
            }
            picking = self.env['stock.picking'].create(picking_vals)

            # Crear movimientos de stock
            for line in self.line_ids:
                move_vals = {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id,
                    'picking_id': picking.id,
                    'location_id': request.location_id.id if request.location_id else request.picking_type_id.default_location_src_id.id,
                    'location_dest_id': request.location_dest_id.id if request.location_dest_id else request.picking_type_id.default_location_dest_id.id,
                    'origin': request.name,
                    'date': line.date_required,
                }
                self.env['stock.move'].create(move_vals)

            # 🟢 Agregar mensaje en el chatter con los productos de new_product_ids
            if request.new_product_ids:
                message = "<b>Productos Nuevos Agregados:</b><br/>"
                for product in request.new_product_ids:
                    message += f"- {product.new_product} ({product.new_description or ''}), Cantidad: {product.new_qty}, UOM: {product.new_uom.name}<br/>"

                picking.message_post(body=message)

            request.write({'picking_id': picking.id, 'state': 'sent'})
        
        
        