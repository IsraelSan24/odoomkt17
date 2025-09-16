from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


_REQUEST_TYPE = [
    ('programado', 'PREVENTIVO'),
    ('no_programado', 'CORRECTIVO'),
    ('consumible', 'CONSUMIBLE'),
    ('reembolsable', 'REEMBOLSABLE'),
    ('activo fijo', 'ACTIVO FIJO')
]

_LOCATIONS = [
    ('uchucchacua', 'UCHUCCHACUA'),
    ('tambomayo', 'TAMBOMAYO'), 
    ('orcopampa', 'ORCOPAMPA'), 
    ('taller', 'TALLER'), 
    ('yumpag', 'YUMPAG'), 
]

_CLASSIFICATION_RFQ = [
    ('service', 'SERVICIO'),
    ('products', 'PRODUCTOS'),
    ('fixed_assets', 'ACTIVO FIJO'),
    ('rental_service', 'SERVICIO DE ALQUILER')
]


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    request_type = fields.Selection(
        string='Tipo de RFQ',
        selection=_REQUEST_TYPE,
        index=True,
        default='programado'
    )
    observations = fields.Text(
        string='Observaciones',
        help='Observaciones del requerimiento',
    )
    document_file = fields.Binary(
        string='Documento',
        attachment=True,
        help='Documento adjunto al requerimiento',
    )
    assigned_to = fields.Many2one(  # Override para modificar el domain en este campo
        string='Approver',
        comodel_name='res.users',
        tracking=True,
        index=True,
        domain=lambda self: [
            '|', '|',
            ('groups_id', 'in', self.env.ref('purchase_request.group_purchase_request_manager').id),
            ('groups_id', 'in', self.env.ref('ind_purchase_request.group_purchase_request_manager_personal').id),
            ('groups_id', 'in', self.env.ref('ind_purchase_request.group_purchase_request_manager_department').id)
        ]
    )
    approved_by = fields.Many2one(
        comodel_name='res.users',
        string='Aprobado por',
        readonly=True,
        copy=False,
        tracking=True,
        index=True,
    )
    date_approved = fields.Datetime(
        string='Fecha de Aprobación',
        readonly=True,
        copy=False,
        tracking=True,
        index=True,
    )
    costo_promedio_total = fields.Monetary(
        string='Coste promedio total',
        compute='_compute_average_total_cost',
        store=True
    )
    classification_rfq = fields.Selection(
        selection=_CLASSIFICATION_RFQ,
        string = 'Clase de RFQ',
    )
    location_id = fields.Selection(
        selection=_LOCATIONS,
        string='Ubicación',
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        tracking=True,
    )
    planning = fields.Boolean( # TODO: DELETE IN V17
        string='Planning Field',
        comodel_name='res.users',
        related='requested_by.planning',
    )
    document_file_name = fields.Char( # TODO: DELETE IN V17
        string='Nombre del Documento',
        size=80
    )

    @api.onchange('classification_rfq', 'location_id')
    def _onchange_eliminated_line(self):
        if self.location_id != self._origin.location_id or self.classification_rfq != self._origin.classification_rfq:
            self.line_ids = [(Command.clear())]
    
    @api.depends('line_ids', 'line_ids.costo_promedio', 'line_ids.cancelled', 'line_ids.request_state')
    def _compute_average_total_cost(self):
        for record in self:
            lines_uncanceled = record.line_ids.filtered(lambda x: x.request_state != 'rejected' and not x.cancelled)
            record.costo_promedio_total = sum(lines_uncanceled.mapped('costo_promedio'))

    def _check_purchase_request(self):
        return all(line.purchase_state in ['cancel', False] for line in self.line_ids)

    def button_to_approve(self):
        for rfq in self:
            if not self.location_id:
                raise UserError("El campo 'Ubicación' es obligatorio.")
            if not self.classification_rfq:
                raise UserError("El camo 'clase' es obligatorio.")
            
            for line in rfq.line_ids:
                if line.product_id.detailed_type == 'consu':
                    raise ValidationError("El producto '{}' esta configurado como consumible".format(line.name))

        return super(PurchaseRequest, self).button_to_approve()
        
    def button_draft(self):
        if self._check_purchase_request():
            self.approved_by = False
            self.date_approved = False
            super(PurchaseRequest, self).button_draft()
        else:
            raise ValidationError('El requerimiento esta asociado a una OC no cancelada')

    def button_approved(self):
        self.approved_by = self.env.user
        self.date_approved = fields.Datetime.now()
        super(PurchaseRequest, self).button_approved()
    
    def copy(self, default=None):
        default = dict(default or {})

        for line in self.line_ids:
            if not line.analytic_distribution:
                raise ValidationError('No se puede duplicar el requerimiento de compra porque contiene líneas sin distribución analítica.')

        default['date_start'] = fields.Date.context_today(self)
        return super(PurchaseRequest, self).copy(default)
    
    def button_rejected(self):
        if self._check_purchase_request():
            self.mapped('line_ids').do_cancel()
            return self.write({'state': 'rejected'})
        else:
            raise ValidationError('El requerimiento esta asociado a una OC no cancelada')

    def print_report_purchase_request(self):
        return self.env.ref('ind_purchase_request.action_print_report_ind_purchase_request').report_action(self)

########################################
# TODO: REFACTOR 3 methods to 1

    # @api.model_create_multi
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         location_code = ''
    #         location_map = {
    #             'uchucchacua': 'UCH',
    #             'tambomayo': 'TBY',
    #             'orcopampa': 'ORC',
    #             'taller': 'TALL',
    #             'yumpag': 'YPG',
    #         }

    #         location_id = vals.get('location_id')
    #         if location_id:
    #             location_code = location_map.get(location_id, '')

    #         now = datetime.now()
    #         year = now.strftime('%Y')
    #         month = now.strftime('%m')
            
    #         # Usamos una única secuencia
    #         seq_number = self.env['ir.sequence'].next_by_code('purchase.request') or '0000'
    #         sequence_number = seq_number[-4:]
    #         # Formato final: RQIUC202504-0191
    #         vals['name'] = f"RQI{location_code}{year}{month}-{sequence_number}"


    #     return super(PurchaseRequest, self).create(vals)

    # @api.onchange('location_id')
    # def _onchange_location_id(self):
    #     if self.location_id:
    #         location_map = {
    #             'uchucchacua': 'UCH',
    #             'tambomayo': 'TBY',
    #             'orcopampa': 'ORC',
    #             'taller': 'TALL',
    #             'yumpag': 'YPG',
    #         }
    #         location_code = location_map.get(self.location_id, '')

    #         now = datetime.now()
    #         year = now.strftime('%Y')
    #         month = now.strftime('%m')

    #         if self.name:
    #             sequence_number = self.name.split('-')[-1]  # Extrae el número de correlativo actual
    #         else:
    #             sequence_number = '0000'
            
    #         self.name = f"RQI{location_code}{year}{month}-{sequence_number}"

    # def write(self, vals):
    #     if 'location_id' in vals:
    #         location_map = {
    #             'uchucchacua': 'UCH',
    #             'tambomayo': 'TBY',
    #             'orcopampa': 'ORC',
    #             'taller': 'TALL',
    #             'yumpag': 'YPG',
    #         }
    #         location_code = location_map.get(vals.get('location_id', self.location_id), '')

    #         now = datetime.now()
    #         year = now.strftime('%Y')
    #         month = now.strftime('%m')

    #         if self.name:
    #             sequence_number = self.name.split('-')[-1]  # Extrae el número de correlativo actual
    #         else:
    #             sequence_number = '0000'
            
    #         vals['name'] = f"RQI{location_code}{year}{month}-{sequence_number}"
        
    #     return super(PurchaseRequest, self).write(vals)