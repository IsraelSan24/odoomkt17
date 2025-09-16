from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


_STATES = [
    ('draft', 'Borrador'),
    ('confirmed', 'Confirmada'),
    ('approved', 'Aprobado'),
    ('done', 'Realizado')
]

_SERVICE_STEPS = [
    ('repair', 'Reparación'),
    ('eval', 'Evaluación'),
]

class ServiceOrder(models.Model):
    _name = 'service.order'
    _description = 'Orden de Trabajo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _order = 'id desc'
    _sql_constraints = [
        ('unique_purchase_request', 'UNIQUE(purchase_request_id)', 'Ya existe una OT con este requerimiento.')
    ]

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code("service.order") or '*'

    @api.model
    def _get_reviewer_id(self, request):
        user_id = request.reviewer_id
        return user_id.partner_id.id

    name = fields.Char(
        string='Referencia de OT',
        required=True,
        default='/',
        copy=False,
        readonly=True,
        tracking=True
    )
    request_date = fields.Datetime(
        string='Fecha de creación',
        default=fields.Datetime.now,
        readonly=True
    )
    requested_by = fields.Many2one(
        string='Solicitante',
        comodel_name='hr.employee',
        required=True,
        tracking=True,
        index=True,
        help='Es el responsable en proponer directamente el diagnostico para que se genere la OT'
    )
    user_id = fields.Many2one(
        string='Generador',
        comodel_name='res.users',
        default=lambda self: self.env.user,
        readonly=True,
        help='Es el responsable en crear la OT directamente en el Odoo de acuerdo lo que indique el solicitante'
    )
    department = fields.Char(
        string='Área',
        related='requested_by.department_id.name',
    )
    job_title = fields.Char(
        string='Cargo',
        related='requested_by.job_title',
    )
    assigned_to = fields.Many2one(
        string='Aprobador',
        comodel_name='res.users',
        required=True,
        tracking=True,
        index=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('ind_service_order.group_service_order_manager').id)],
        help='Es el responsable en aprobar la OT'
    )
    approval_date = fields.Datetime(
        string='Fecha de aprobación',
        readonly=True
    )
    state = fields.Selection(
        string='Estado',
        default='draft',
        tracking=True,
        selection=_STATES
    )
    description = fields.Char(string='Descripción OT')
    purchase_request_id = fields.Many2one(
        comodel_name='purchase.request',
        string='Requerimiento'
    )
    purchase_request_line_ids = fields.Many2many(
        comodel_name='purchase.request.line',
        string='Estados de las OC',
        compute='_compute_related_state',
        copy=False,
        store=True
    )
    purchase_request_state = fields.Selection(
        related='purchase_request_id.state', 
        string='Estado del Requerimiento', 
        store=True
    )
    show_reset_draft = fields.Boolean(
        compute='_compute_show_reset_draft',
        store=False
    )
    purchase_request_count = fields.Integer(compute='_compute_purchase_request_count')
    quote_check = fields.Boolean(
        string='Cotización',
        compute='_compute_cotizacion_date_check'
    )
    oc_check = fields.Boolean(
        string='Orden de Compra',
        compute='_compute_orden_compra_check',
    )
    delivery_from_supplier_check = fields.Boolean(
        string='Entrega del Proveedor',
        compute='_compute_delproveedor_date_check'
    )
    supplier_report_check = fields.Boolean(
        string='Informe Proveedor',
        compute='_compute_informeproveedor_date_check'
    )
    conformity_service_check = fields.Boolean(
        string='Conformidad Servicio',
        compute='_compute_state_conformity'
    )
    invoice_check = fields.Boolean(
        string='Factura',
        compute='_compute_invoice_check'
    )
    documentary_review_check = fields.Boolean(string='Revisión Documentaria')
    delivery_to_supplier_check = fields.Boolean(
        string='Entrega al Proveedor',
        compute='_compute_alproveedor_date_check'
    )
    quote_date = fields.Datetime(readonly=True)
    rfq_date = fields.Datetime(readonly=True)
    oc_date = fields.Datetime(readonly=True)
    delivery_supplier_date = fields.Datetime(readonly=True)
    supplier_report_date = fields.Datetime(readonly=True)
    conformity_service_date = fields.Datetime(readonly=True)
    invoice_date = fields.Datetime(readonly=True)
    documentary_review_date = fields.Datetime(readonly=True)
    delivery_to_supplier_date = fields.Datetime(readonly=True)
    rfq_check = fields.Boolean(
        string='Requerimiento',
        compute='_compute_requerimiento_check',
    )
    service_conformity_id = fields.One2many(
        comodel_name='service.conformity',
        inverse_name='service_order_id',
        string='Orden de Conformidad'
    )
    equipment_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Equipo (Centro de Costo)',
        domain=[('active', '=', True)],  # Solo muestra centros de costo activos
        help='Seleccione el centro de costo que corresponde al equipo.'
    )
    equipment_model = fields.Char(
        string='Modelo',
        # related='equipment_id.model'
    )
    equipment_serie = fields.Char(
        string='Número de Serie',
        # related='equipment_id.serie'
    )
    equipment_brand = fields.Char(
        string='Marca',
        # related='equipment_id.brand'
    )
    equipment_hourmeter = fields.Float(
        string='Horómetro',
        # related='equipment_id.hour_meter'
    )
    company_id = fields.Many2one(
        comodel_name='res.company', 
        string="Compañia", 
        required=True, 
        default=lambda self: self.env.company
    )
    company_selection_enabled = fields.Boolean(compute='_compute_company_selection_enabled')
    component_id = fields.Many2one(
        comodel_name='product.product',
        string='Componente',
        domain=[('type', '!=', 'service')],
        help='Seleccione un producto como componente asociado.'
    )
    component_model = fields.Char(string='Modelo')
    component_brand = fields.Char(string='Marca')
    component_hourmeter = fields.Float(string='Horómetro')
    component_serie = fields.Char(string='Número de Parte')
    service_steps = fields.Selection(
        string='Servicio',
        default='repair',
        selection=_SERVICE_STEPS,
    )
    comments = fields.Text(
        string='Comentarios',
        help='En este campo se tiene que detallar especificaciones tecnicas del trabajo a realizar'
    )
    # Imagen adjunta
    image_technical = fields.Image(
        string='Imagen Adicional',
        max_width=340,
        max_height=340
    )
    attachment_technical_report = fields.Binary(
        string='Reporte técnico',
        attachment=True,
    )
    # Relación con piezas requeridas
    parts_required_ids = fields.One2many(
        comodel_name='service.order.part',
        inverse_name='service_order_id',
        string='Piezas Requeridas'
    )

    #cotizacion 
    quote_report = fields.Binary(
        string='Actas de Cotizacion',
        attachment=True,
        
    )
    #informes
    supplier_delivery_report = fields.Binary(
        string='Acta de Entrega del Proveedor',
        attachment=True,
        
    )
    delivery_to_supplier_report = fields.Binary(
        string='Acta de Entrega para el Proveedor',
        attachment=True,
        
    )
    supplier_report = fields.Binary(
        string='Informe del Proveedor',
        attachment=True,
        
    )
    
    @api.depends("purchase_request_id.line_ids")
    def _compute_related_state(self):
        """Calcula todas las líneas de órdenes de compra relacionadas a la orden de servicio"""
        for record in self:
            if record.purchase_request_id:
                purchase_lines_ids = record.purchase_request_id.mapped("line_ids").ids
                record.purchase_request_line_ids = [(6, 0, purchase_lines_ids)] if purchase_lines_ids else [(5, 0, 0)]
            else:
                record.purchase_request_line_ids = [(5, 0, 0)]  # Limpia si no hay datos 
    
    @api.depends("state", "purchase_request_id", "purchase_request_state")
    def _compute_show_reset_draft(self):
        """Determina si el botón debe mostrarse o no."""
        for record in self:
            if not record.purchase_request_id:
                record.show_reset_draft = record.state in ["confirmed", "approved"]
            else:
                record.show_reset_draft = record.purchase_request_state == "rejected" and record.state in ["confirmed", "approved"] 
    
    @api.depends('purchase_request_state')
    def _compute_requerimiento_check(self):
        for record in self:
            record.rfq_check = record.purchase_request_state == 'approved'
            if record.rfq_check:
               record.rfq_date = fields.Datetime.now()

    @api.depends("purchase_request_line_ids.purchase_state", "purchase_request_line_ids.request_state")
    def _compute_orden_compra_check(self):
      """Verifica si todas las líneas de órdenes de compra están en estado 'purchase', 
       ignorando aquellas cuyo request_state es 'rejected'"""
      for record in self:
        purchase_lines_validas = record.purchase_request_line_ids.filtered(lambda line: line.request_state != "rejected")
        estados = purchase_lines_validas.mapped("purchase_state")
        record.oc_check = all(state == "purchase" for state in estados) if estados else False
        if record.oc_check:
            record.oc_date = fields.Datetime.now()

    @api.depends("service_conformity_id.state")
    def _compute_state_conformity(self):
        for record in self:
            record.conformity_service_check = any(
               conformity.state == 'approved' for conformity in record.service_conformity_id
             )
            if record.conformity_service_check:
                record.conformity_service_date = fields.Datetime.now()
            else: 
                record.conformity_service_date = False   
    
    @api.depends("purchase_request_line_ids.purchase_lines.order_id.invoice_ids.state")
    def _compute_invoice_check(self):
        for record in self:
            invoices = record.purchase_request_line_ids.purchase_lines.order_id.mapped("invoice_ids")
            if invoices:
              record.invoice_check = all(invoice.state == 'posted' for invoice in invoices)
            else:
              record.invoice_check = False

    @api.depends('company_id')
    def _compute_company_selection_enabled(self):
        """Habilita o deshabilita la selección de empresa según el número de compañías del usuario."""
        for record in self:
            record.company_selection_enabled = len(self.env.user.company_ids) > 1
    
    @api.model_create_multi
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self._get_default_name()
        service = super(ServiceOrder, self).create(vals)
        if vals.get('reviewer_id'):
            reviewer_id = self._get_reviewer_id(service)
            service.message_subscribe(partner_ids=[reviewer_id])
        return service
    
    @api.depends('purchase_request_id')
    def _compute_purchase_request_count(self):
        for rec in self:
            rec.purchase_request_count = 1 if rec.purchase_request_id else 0

    def action_confirm(self):
        """ Cambiar estado a confirmado """
        for rec in self:
            if not rec.attachment_technical_report:
                raise UserError('Debe adjuntar un reporte técnico antes de confirmar la orden de servicio.')
            rec.state = 'confirmed'

    def action_approve(self):
        """ Cambiar estado a aprovado """
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError('Solo se puede aprobar una orden de servicio confirmada.')
            if self.env.user.id != rec.assigned_to.id:
                raise ValidationError('Solo el aprobador asignado puede aprobar la orden de servicio.')
            rec.state = 'approved'
            rec.approval_date = fields.Datetime.now()

    def action_done(self):
        """ Cambiar estado a hecho """
        for rec in self:
           rec.state = 'done'

    def action_reset_draft(self):
        """ Cambiar estado a borrador """
        for rec in self:
            if rec.state in ('proved', 'done'):
                raise UserError('No se puede regresar a borrador una orden de servicio que ya ha sido aprobada o realizada.')
            rec.state = 'draft'

    def action_view_purchase_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requerimiento',
            'view_mode': 'form',
            'res_model': 'purchase.request',
            'res_id': self.purchase_request_id.id,
            'target': 'current'
        }

    def action_create_rfq(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError('Solo se puede crear una solicitud de compra para una OT aprobada.')
            if rec.purchase_request_id.state:
                raise UserError('Ya existe una solicitud de compra para esta OT.')
            purchase_request = self.env['purchase.request'].create({
                'name': self.env["ir.sequence"].next_by_code("purchase.request"),
                'requested_by': self.user_id.id,
                'origin': self.name,
                'request_type': 'programado',
            })

            self.purchase_request_id = purchase_request.id
            self.message_post(
                body=f'Se creó la solicitud de compra {purchase_request.name} vinculada a : {self.name}.'
            )

    def action_open_conformity(self):
        """Abre o crea un registro en service.conformity vinculado con la orden de servicio."""
        self.ensure_one()

        # Buscar si ya existe una conformidad asociada
        conformity = self.env["service.conformity"].search([("service_order_id", "=", self.id)], limit=1)

        # Si no existe, se crea automáticamente
        if not conformity:
            conformity = self.env["service.conformity"].create({
                "service_order_id": self.id,  # Relaciona con la orden de servicio
            })

        # Abrir el formulario de service.conformity
        return {
            "name": "Conformidad de Servicio",
            "type": "ir.actions.act_window",
            "res_model": "service.conformity",
            "view_mode": "form",
            "res_id": conformity.id,
            "target": "current",
        }
    
    @api.depends('quote_report')
    def _compute_cotizacion_date_check(self):
        """Activa el check y guarda la fecha al subir un archivo. Desactiva ambos si se elimina."""
        for record in self:
            if record.quote_report:
                record.quote_check = True
                if not record.quote_date:  # Evita actualizar la fecha si ya existe
                   record.quote_date = fields.Datetime.now()
            else:
                record.quote_check = False
                record.quote_date = False


    @api.depends('delivery_to_supplier_report')
    def _compute_alproveedor_date_check(self):
        """Activa el check y guarda la fecha al subir un archivo. Desactiva ambos si se elimina."""
        for record in self:
            if record.delivery_to_supplier_report:
                record.delivery_to_supplier_check = True
                if not record.delivery_to_supplier_date:
                   record.delivery_to_supplier_date = fields.Datetime.now()
            else:
                record.delivery_to_supplier_check = False
                record.delivery_to_supplier_date = False

    @api.depends('supplier_delivery_report')
    def _compute_delproveedor_date_check(self):
        """Activa el check y guarda la fecha al subir un archivo. Desactiva ambos si se elimina."""
        for record in self:
            if record.supplier_delivery_report:
                record.delivery_from_supplier_check = True
                if not record.delivery_supplier_date:
                   record.delivery_supplier_date = fields.Datetime.now()  
            else:
                record.delivery_from_supplier_check = False
                record.delivery_supplier_date = False

    @api.depends('supplier_report')
    def _compute_informeproveedor_date_check(self):
        """Activa el check y guarda la fecha al subir un archivo. Desactiva ambos si se elimina."""
        for record in self:
            if record.supplier_report:
                record.supplier_report_check = True
                if not record.supplier_report_date:
                    record.supplier_report_date = fields.Datetime.now()
            else:
                record.supplier_report_check = False
                record.supplier_report_date = False
