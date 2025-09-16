from odoo import models, fields, api
from odoo.exceptions import UserError

_STATES = [
    ('draft', 'Borrador'),
    ('confirmed', 'Confirmada'),
    ('cancelled', 'Cancelada'),
    ('done', 'Recogido'),
]

_REQUEST_TYPE = [
    ('product', 'Producto'),
    ('service', 'Servicio'),
    ('active', 'Activo')
]

_MODALITY = [
    ('pickup', 'Recojo'),
    ('reception', 'Recepción'),
    ('delivery', 'Envío'),
    ('supplier_pickup', 'Proveedor Recoje'),
    ('regularization', 'Regularización')
]

_URGENCY = [
    ('moderate', 'Moderado'),
    ('urgent', 'Urgente'),
    ('critical', 'Crítico')
]

_STATUS = [
    ('in_route', 'En Ruta'),
    ('rescheduled', 'Reprogramado'),
    ('in_warehouse', 'En Almacén'),
    ('at_supplier', 'En Proveedor'),
    ('pending_pickup', 'Falta Recoger'),
    ('partial_pickup', 'Se Recogió OC Incompleta'),
    ('canceled_by_purchases', 'OC Cancelada por Compras')
]

_LIQUIDATION_STATUS = [
    ('delivered', 'Entregado'),
    ('sent_to_juan', 'Enviado a Juan'),
    ('sent_to_luis_p', 'Enviado a Luis P.'),
    ('sent_to_carlos_romero', 'Enviado a Carlos Romero')
]


class PickupRequest(models.Model):
    _name = 'pickup.request'
    _description = 'Pickup Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    #Estado de recogo 
    state = fields.Selection(
        selection=_STATES,
        string='Estado',
        default='draft',
        tracking=True
    )
    pickup_datetime = fields.Datetime(
        string='Fecha y Hora de Solicitud',
        readonly=True
    )
    accounting_delivery_date = fields.Datetime(
        string='Fecha de entrega Contabilidad',
        readonly=True,
        default=False,
        compute='_compute_accounting_delivery_date',  # actualiza el valor accounting_delivery_date cuando liquidation_status cambia de estado 
        store=True
    )
    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Orden de compra', 
        required=True, 
        readonly=True
    )
    purchase_order_line_ids = fields.Many2many(
        comodel_name='purchase.order.line', 
        string='Líneas de la orden de compra',
        domain="[('order_id', '=', purchase_order_id)]"  # Filtra las líneas según la orden de compra seleccionada
    )
    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        string='Ingresos',
        compute='_compute_picking_ids',
        store=True,
        readonly=True  # Evitar la edición manual
    )
    request_type = fields.Selection(
        selection=_REQUEST_TYPE,
        string='Tipo',
        required=True
    )
    modality = fields.Selection(
        selection=_MODALITY,
        string='Modalidad',
        required=True,
        tracking=True
    )
    urgency = fields.Selection(
        selection=_URGENCY,
        string='Grado de Urgencia',
        required=True,
        tracking=True
    )
    observations = fields.Text(
        string='Observaciones',
        tracking=True
    )
    purchase_request_ids = fields.Many2many(
        comodel_name='purchase.request', 
        string='RFQs Origen', 
        compute='_compute_purchase_request_ids', 
        store=True,tracking=True
    )
    requested_by = fields.Many2many(
        comodel_name='res.users',
        string='Solicitado por',
        compute='_compute_requested_by',
        store=True,
        readonly=True  # Evita edición manual
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner', 
        string='Proveedor', 
        related='purchase_order_id.partner_id', 
        store=True
    )
    # Relación al campo VAT del proveedor
    partner_vat = fields.Char(
        string='RUC/ID del Proveedor', 
        related='partner_id.vat', 
        store=True
    )
    # Relación al campo dirección del proveedor
    partner_street = fields.Char(
        string='Dirección del Proveedor', 
        related='partner_id.street', 
        store=True
    )
    delivery_address_id = fields.Many2one(
        comodel_name='partner.delivery.address',
        string='Dirección de Entrega',
        domain="[('partner_id', '=', partner_id)]",
        required=False,
        tracking=True
    )
    driver_id = fields.Many2one(
        comodel_name='hr.employee', 
        string='Conductor', 
        domain="[('job_title', '=', 'Conductor')]",
        required=False,
        tracking=True
    )
    warehouse_observations = fields.Text(string='Observaciones de Almacén', tracking=True)
    company_id = fields.Many2one(
        'res.company', 
        string='Compañia', 
        required=True, 
        default=lambda self: self.env.company
    )
    status = fields.Selection(
        selection=_STATUS,
        string='Estado',
        default='pending_pickup',
        tracking=True
    )
    guia = fields.Char(
        string='Guía',
        compute='_compute_picking_info',
        store=True,
        readonly=True
    )
    date_done = fields.Datetime(
        string='Fecha de Ingreso',
        compute='_compute_picking_info',
        store=True,
        readonly=True
    )
    days_difference = fields.Integer(
        string='Diferencia en días',
        compute='_compute_days_difference'
    )
    liquidation_status = fields.Selection(
        selection=_LIQUIDATION_STATUS,
        string='Estado de Liquidación',
        tracking=True
    )
    invoice_number = fields.Char(
        string='Número de Factura',
        help='Número de factura asociado a la solicitud de recojo. No está vinculado a la contabilidad.',
        tracking=True
    )
    work_time = fields.Char(
        related='partner_id.street2',
        string='Horario Laboral',
        store=True
    )
    company_selection_enabled = fields.Boolean(compute='_compute_company_selection_enabled')
    datetime_recogido = fields.Datetime(
        string='Fecha y Hora de Recogo',
        compute='_compute_datetime_recogido',
        readonly=True,
        store=True
    )


    @api.depends('company_id')
    def _compute_company_selection_enabled(self):
        '''Habilita o deshabilita la selección de empresa según el número de compañías del usuario.'''
        for record in self:
            record.company_selection_enabled = len(self.env.user.company_ids) > 1

    ##
    @api.depends('state')
    def _compute_datetime_recogido(self):
        for record in self:
            if record.state == 'done' and not record.datetime_recogido:
                   record.datetime_recogido = fields.Datetime.now()
            else:
                record.datetime_recogido = False    
    ##
    @api.depends('liquidation_status')
    def _compute_accounting_delivery_date(self):
        print('ESTOY PASANDO POR EL MÉTODO LIQUIDATION STATUS')
        for rec in self:
            if rec.liquidation_status == 'delivered':
                rec.accounting_delivery_date = fields.Datetime.now()
            else:
                rec.accounting_delivery_date = False
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        '''Actualizar las direcciones disponibles para el proveedor.'''
        if self.partner_id:
            # Si el proveedor cambia, limpiar la dirección seleccionada
            self.delivery_address_id = False
        else:
            self.delivery_address_id = False
                
    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        if self.purchase_order_id:
            self.purchase_order_line_ids = [(6, 0, self.purchase_order_id.order_line.ids)]
        else:
            self.purchase_order_line_ids = [(5, 0)]  # Limpia las líneas si no hay OC seleccionada
    
    # Sobrescribir create para asegurar que se tome la OC actual y las líneas relacionadas
    @api.model_create_multi
    def create(self, vals):
        # Obtener la hora actual del sistema
        current_datetime = fields.Datetime.now()
        vals['pickup_datetime'] = current_datetime

        # Verificar si existe una orden de compra relacionada
        if vals.get('purchase_order_id'):
            purchase_order = self.env['purchase.order'].browse(vals['purchase_order_id'])

            # Asignar las líneas de la orden de compra a purchase_order_line_ids
            vals['purchase_order_line_ids'] = [(6, 0, purchase_order.order_line.ids)]

            # Buscar el primer picking relacionado a la orden en estado realizado
            pickings = self.env['stock.picking'].search([
                ('purchase_id', '=', purchase_order.id),
                ('state', '=', 'done')  # Filtrar por estado 'realizado'
            ], order='id asc', limit=1)  # Tomar el primero por orden de creación

            # Asignar el picking encontrado al campo picking_ids
            vals['picking_ids'] = [(6, 0, pickings.ids)]

        # Si se seleccionó una dirección personalizada, asegurarse de que esté vinculada al proveedor
        if 'partner_id' in vals and 'delivery_address_id' in vals:
            delivery_address = self.env['partner.delivery.address'].browse(vals['delivery_address_id'])
            if delivery_address.partner_id.id != vals['partner_id']:
                raise UserError('La dirección seleccionada no pertenece al proveedor seleccionado.')

        # Si no hay una dirección seleccionada, crear una predeterminada basada en la dirección del proveedor
        if 'partner_id' in vals and not vals.get('delivery_address_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            default_address = self.env['partner.delivery.address'].create({
                'name': partner.street or 'Dirección desconocida',
                'partner_id': partner.id
            })
            vals['delivery_address_id'] = default_address.id

        # Crear el registro en la base de datos
        res = super(PickupRequest, self).create(vals)

        # Actualizar el campo street2 en res.partner si se proporciona work_time
        if 'partner_id' in vals and 'work_time' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            partner.street2 = vals['work_time']  # Actualizar el horario laboral en el proveedor.

        return res

    def write(self, vals):

        if 'partner_id' in vals and 'work_time' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            partner.street2 = vals['work_time']

        return super(PickupRequest, self).write(vals)

    @api.depends('purchase_order_id', 'purchase_order_id.picking_ids.state')
    def _compute_picking_ids(self):
        for request in self:
            if request.purchase_order_id:
                # Buscar el primer picking relacionado en estado 'done'
                pickings = self.env['stock.picking'].search([
                    ('purchase_id', '=', request.purchase_order_id.id),
                    ('state', '=', 'done')  # Solo los pickings en estado realizado
                ], order='id asc', limit=1)

                request.picking_ids = [(6, 0, pickings.ids)]
            else:
                request.picking_ids = [(5, 0)]  # Limpiar si no hay purchase_order_id

    @api.depends('picking_ids', 'picking_ids.date_done', 'picking_ids.guia')
    def _compute_picking_info(self):
        for record in self:
            if record.picking_ids:
                # Tomar el primer picking (relacionado)
                picking = record.picking_ids[:1]
                # Si se encuentra un picking, asignar los valores
                if picking:
                    record.guia = picking.guia if hasattr(picking, 'guia') else False
                    record.date_done = picking.date_done if hasattr(picking, 'date_done') else False
                else:
                    record.guia = False
                    record.date_done = False
            else:
                record.guia = False
                record.date_done = False
    
    def confirm_pickup(self):
        # Verificar que todos los campos estén llenos antes de confirmar
        if not self.purchase_order_line_ids:
            raise UserError('Debes seleccionar al menos una línea de la orden de compra.')
        if not self.picking_ids:
            raise UserError('No hay transferencias relacionadas con esta orden de compra.')
        if not self.request_type:
            raise UserError('Debes seleccionar el tipo de solicitud.')
        if not self.modality:
            raise UserError('Debes seleccionar la modalidad de la solicitud.')
        if not self.urgency:
            raise UserError('Debes seleccionar el grado de urgencia.')
        
        # Lógica de confirmación de la solicitud de recojo (puedes agregar cualquier otra acción aquí)
        return True
    
    @api.depends('create_date', 'date_done')
    def _compute_days_difference(self):
        for request in self:
            if request.date_done and request.create_date:
                delta = request.date_done.date() - request.create_date.date()
                request.days_difference = delta.days
            else:
                request.days_difference = 0

    @api.depends('purchase_order_id')
    def _compute_purchase_request_ids(self):
        for record in self:
            if record.purchase_order_id:
                # Obteniendo todos los IDs de purchase.request relacionados con la orden de compra
                self.env.cr.execute('''
                    SELECT purchase_request_id 
                    FROM purchase_order_purchase_request_rel 
                    WHERE purchase_order_id = %s
                ''', (record.purchase_order_id.id,))
                result = self.env.cr.fetchall()
                
                # Asignar los IDs obtenidos al campo purchase_request_ids
                record.purchase_request_ids = [(6, 0, [r[0] for r in result])] if result else [(5, 0)]
            else:
                record.purchase_request_ids = [(5, 0)]  # Limpiar si no hay purchase_order_id
    
    def action_view_purchase_order(self):

       self.ensure_one()  # Asegura que solo haya un registro seleccionado
       action = self.env['ir.actions.actions']._for_xml_id('purchase.purchase_rfq')

    # Obtener las órdenes de compra relacionadas
       purchase_orders = self.mapped('purchase_order_id')

       if len(purchase_orders) > 1:
           action['domain'] = [('id', 'in', purchase_orders.ids)]  # Mostrar varias órdenes en vista lista
       elif purchase_orders:
        action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        action['res_id'] = purchase_orders.id  # Abrir la OC directamente en vista formulario

       return action



    @api.depends('purchase_request_ids')
    def _compute_requested_by(self):
        for record in self:
            if record.purchase_request_ids:
                # Obtener todos los usuarios solicitantes de los requerimientos relacionados
                user_ids = record.purchase_request_ids.mapped('requested_by.id')
                record.requested_by = [(6, 0, user_ids)]
            else:
                record.requested_by = [(5, 0)]  # Limpiar si no hay requerimientos relacionados

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_done(self):
        for record in self:
            record.state = 'done'

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'

    def action_draft(self):
        for record in self:
            record.state = 'draft'
            
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        '''Cargar el horario laboral del proveedor cuando se seleccione.'''
        if self.partner_id:
            self.work_time = self.partner_id.street2  # Cargar el horario laboral desde street2.

    def print_purchase_order(self):
        self.ensure_one()
        if self.purchase_order_id:
            return self.env.ref('purchase.action_report_purchase_order').report_action(self.purchase_order_id)

