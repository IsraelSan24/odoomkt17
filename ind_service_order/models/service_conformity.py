from odoo import models, fields, api
from odoo.exceptions import UserError

_STATES_ORDER = [
    ('draft', 'Borrador'),
    ('confirmed', 'Solicitado'),
    ('approved', 'Aprobado'),
]

_STATES_QUALITY = [
    ('excellent', 'EXCELENTE'),
    ('good', 'BUENO'),
    ('regular', 'POR MEJORAR')
]


class ServiceConformity(models.Model):
    _name = 'service.conformity'
    _description = 'Conformidad del Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string='Conformidad de servicio',
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('service.conformity') or '*',
        copy=False
    )
    state = fields.Selection(
        string='Estado',
        default='draft',
        tracking=True,
        selection=_STATES_ORDER
    )
    service_order_id = fields.Many2one(
        comodel_name='service.order', 
        string='Orden de Trabajo', 
        help='Relaciona la conformidad del servicio con una orden de trabajo específica'
    )
    application_date = fields.Datetime(
        string='Fecha de Solicitud',
        readonly=True
    )
    approval_date = fields.Datetime(
        string='Fecha de Aprobación',
        readonly=True
    )
    requested_by = fields.Many2one(
        string='Solicitante',
        related='service_order_id.requested_by',
        readonly=True
    )
    department = fields.Char(
        string='Departamento',
        related='requested_by.department_id.name',
        readonly=True
    )
    job_title = fields.Char(
        string='Cargo',
        related='requested_by.job_title',
        readonly=True
    )
    email = fields.Char(
        string='Correo Electrónico',
        related='requested_by.work_email',
        readonly=True
    )
    create_date_ot = fields.Datetime(
        string='Fecha de Solicitud de la OT',
        compute='_compute_fecha_creacion_ot',
        store=True
    )
    approval_date_ot = fields.Datetime(
        string='Fecha de Aprobación de la OT',
        compute='_compute_fecha_aprobacion_ot',
        store=True
    )
    warehouse_delivery_date = fields.Datetime(
        string='Fecha de Entrega de Almacen',
        compute='_compute_fecha_almacen',
        store=True
    )
    currency_id = fields.Many2one(
        string='Moneda',
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id
    )
    total_cost = fields.Monetary(
        string='Coste Total del Servicio',
        currency_field='currency_id',
        store=True
    )
    quality_service = fields.Selection(
        string='Calidad del Servicio',
        selection=_STATES_QUALITY,
    )
    requesting_signature = fields.Binary(string='Firma del Solicitante')
    purchase_order_line_ids = fields.Many2many(
        comodel_name='purchase.order.line',
        string='Lista de las OC',
        compute='_compute_related_state',
        copy=False,
        store=True
    )
    purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order',
        string='Lista de las OC',
        compute='_compute_coste_total',
        copy=False,
        store=True
    )
    pickup_order_ids = fields.Many2many(
        comodel_name='pickup.request',
        string='Lista de recogo',
        compute='_compute_recogo_total',
        copy=False,
        store=True
    )

    @api.depends('service_order_id.delivery_to_supplier_check')
    def _compute_fecha_almacen(self):
        for record in self:
            if record.service_order_id.delivery_to_supplier_check:
              record.warehouse_delivery_date = record.service_order_id.delivery_to_supplier_date
            else:
               record.warehouse_delivery_date = False

    @api.depends('service_order_id.purchase_request_id.line_ids.request_state')
    def _compute_related_state(self):
        '''Calcula todas las líneas de órdenes de compra relacionadas a la orden de servicio con estado 'purchase' y solicitudes aprobadas.'''
        for record in self:
           if record.service_order_id:
               purchase_lines = record.service_order_id.purchase_request_id.mapped('line_ids')
               purchase_lines_approved = purchase_lines.filtered(
                   lambda line: line.purchase_state == 'purchase'
               ).mapped('purchase_lines')
               
               record.purchase_order_line_ids = [(6, 0, purchase_lines_approved.ids)] if purchase_lines_approved else [(5, 0, 0)]
           else:
               record.purchase_order_line_ids = [(5, 0, 0)]  # Limpia si no hay datos

    @api.depends('purchase_order_line_ids.order_id')
    def _compute_coste_total(self):
       '''Calcula el coste total utilizando el valor almacenado en 'tax_totals_json'.'''
       for record in self:
           if record.purchase_order_line_ids:
               purchase_lines = record.purchase_order_line_ids.mapped('order_id')
               record.purchase_order_ids = purchase_lines.filtered(
                   lambda line: line.state == 'purchase'
               )
               record.purchase_order_line_ids = record.purchase_order_line_ids.filtered(
                  lambda line: line.order_id.id in record.purchase_order_ids.mapped('id')
               ) 
               record.total_cost = sum(record.purchase_order_ids.mapped('amount_untaxed'))
           else:
               record.purchase_order_line_ids = [(5, 0, 0)]  # Limpia si no hay datos
               record.total_cost = 0.0   

    @api.depends('purchase_order_ids.pickup_request_ids')
    def _compute_recogo_total(self):
        for record in self:
            if record.purchase_order_ids:
                record.pickup_order_ids = record.purchase_order_ids.mapped('pickup_request_ids')
            else:
                record.pickup_order_ids = [(5, 0, 0)]

    @api.depends('requested_by')
    def _compute_cargo(self):
        for record in self:
            employee = record.requested_by.employee_id
            record.job_title = employee.job_id.name if employee and employee.job_id else False
    
    @api.depends('service_order_id.approval_date')
    def _compute_fecha_aprobacion_ot(self):
        for record in self:
            record.approval_date_ot = record.service_order_id.approval_date
    
    @api.depends('service_order_id.request_date')
    def _compute_fecha_creacion_ot(self):
        for record in self:
            record.create_date_ot = record.service_order_id.request_date

    def toggle_edit_mode(self):
        ''' Activa el modo edición del formulario '''
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'service.conformity',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'flags': {'form': {'edit': True}}  # Esta bandera activa el modo edición
        }

    def action_confirm(self):
        ''' Confirma el registro solo si `service_order_id` existe y asigna la fecha actual '''
        for record in self:
            if not record.service_order_id:
                raise UserError("No puedes confirmar sin una 'Orden de Servicio' asociada.")
            if not record.requesting_signature:
                raise UserError('Falta la firma del solicitante')
            if not record.quality_service:
                raise UserError('Falta la calidad del servicio')

            # Asignar la fecha actual en `fecha_solicitud`
            record.state = 'confirmed'
            record.application_date = fields.Datetime.now()
    
    def action_approved(self):
        ''' Confirma el registro solo si `service_order_id` existe y asigna la fecha actual '''
        for record in self:
            # Asignar la fecha actual en `fecha_solicitud`
            record.state = 'approved'
            record.approval_date = fields.Datetime.now()
            
    def toggle_edit_mode(self):
        """Regresa el estado a 'draft'"""
        for record in self:
            record.state = 'draft'
    