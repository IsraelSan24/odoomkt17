from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError

_ORDER_STATUS = [
    ('pago', 'Área de pago'),
    ('transporte', 'Área de Transporte'),
    ('proveedor', 'Proveedor trae'),
    ('almacen', 'En almacén'),
    ('regularización', 'Regularización'),
    ('en_aprobacion', 'En aprobación')
]

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_status = fields.Selection(
        string='Estado de pedido',
        selection=_ORDER_STATUS,
        index=True,
        default=False
    )
    view_notes = fields.Boolean(string='Imprimir Notas')
    inverse_rate = fields.Float(
        string='Tipo de cambio',
        digits=(9, 3),
        default=1.0,
        store=True,
        compute='_compute_exchange_rate',
    )
    purchase_request_related = fields.Many2many(
        string='RFQs Relacionadas',
        comodel_name='purchase.request',
        compute='_compute_purchase_request_ids_count',
        store=True
    )
    rfq_related_count = fields.Integer(
        string='RFQs de Origen',
        compute='_compute_purchase_request_ids_count',
        store=True
    )
    date_picking = fields.Datetime(
        string='Fecha de recojo',
        tracking=True,
        store=True
    )
    taxes_id = fields.Many2many(
        comodel_name='account.tax',
        string='Impuestos',
        domain=[('active', '=', True)]
    )
    global_discount = fields.Float(
        string='Descuento global (%)',
        default=0.0
    )
    first_request_id = fields.Many2one(
        string='First Purchase Request',
        comodel_name='purchase.request',
        compute='_compute_first_request',
        store=True
    )
    request_type = fields.Selection(
        related='first_request_id.request_type',
        string='Tipo de RFQ',
        store=False,
        readonly=True
    )
    classification_rfq = fields.Selection(
        related='first_request_id.classification_rfq',
        string='Clase de RFQ',
        store=False,
        readonly=True
    )
    location_id = fields.Selection(
        related='first_request_id.location_id',
        string='Ubicación',
        store=False,
        readonly=True
    )
    fake_inverse_rate = fields.Float( # TODO: DELETE IN V17
        string='Tipo de cambio falso',
        store=True,
        digits=(9,3)
    )

    @api.depends('purchase_request_related')
    def _compute_first_request(self):
        for order in self:
            # Tomar el primer request (por orden de ID más pequeño)
            order.first_request_id = order.purchase_request_related and order.purchase_request_related.sorted('id')[0] or False

    @api.onchange('global_discount')
    def _onchange_global_discount(self):
        for order in self:
            for line in order.order_line:
                line.discount = order.global_discount

    @api.depends('currency_id')
    def _compute_exchange_rate(self):
        for record in self:
            currency_usd = self.env['res.currency'].search([
                ('name', '=', 'USD'),
                ('active', '=', True)
            ], limit=1)

            date = record.date_approve or record.date_order or fields.Date.today()
            currency_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', currency_usd.id),
                ('name', '=', date),
                ('company_id', '=', record.company_id.id)
            ], limit=1)

            if not currency_rate.rate and currency_rate.inverse_company_rate:
                raise ValidationError("No se encontró tipo de cambio para la fecha '{}' en la OC: '{}'".format(date, record.name))

            record.inverse_rate = currency_rate.inverse_company_rate

    @api.depends('order_line.purchase_request_lines.request_id')
    def _compute_purchase_request_ids_count(self):
        for record in self:
            rfq_ids = record.order_line.mapped('purchase_request_lines.request_id')
            record.purchase_request_related = [Command.set(rfq_ids.ids)]
            record.rfq_related_count = len(rfq_ids)

    @api.onchange('taxes_id')
    def _onchange_tax_ids(self):
        for record in self:
            if record.taxes_id and record.order_line:
                record.order_line.update({
                    'taxes_id': [Command.set(record.taxes_id.ids)]
                })

    def button_draft(self):
        for order in self:
            for line in order.order_line:
                total_requested = sum(req_line.product_qty for req_line in line.purchase_request_lines
                    if req_line.product_id == line.product_id)

                # Total comprado en otras órdenes de compra (activas) asociadas a las mismas líneas de solicitud
                po_lines = self.env['purchase.order.line'].search([
                    ('id', '!=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('purchase_request_lines', 'in', line.purchase_request_lines.ids),
                    ('state', '!=', 'cancel')
                ])

                total_ordered = sum(l.product_qty for l in po_lines)
                # Si al reabrir esta OC se sobrepasa lo requerido → error
                if total_ordered + line.product_qty > total_requested:
                    raise ValidationError(
                        f'❌ No puedes reabrir esta orden: el producto "{line.product_id.display_name}" '
                        f'superaría la cantidad solicitada ({total_requested}). '
                        f'Ya se han ordenado {total_ordered}.'
                    )

                allocations = self.env['purchase.request.allocation'].search([
                    ('purchase_line_id', '=', line.id)
                ])

                for allocation in allocations:
                    request_state = allocation.purchase_request_line_id.request_state
                    if request_state in ['rejected','draft','to_approve']:
                        raise ValidationError("No se puede cambiar a borrador porque la solicitud no esta aprobada")
                    else:
                        self.write({'state': 'draft'})
                        return {}

    def action_view_purchase_request(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Solicitudes de compra',
            'res_model': 'purchase.request',
            'target': 'current',
        }

        if len(self.purchase_request_related) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.purchase_request_related.id,
            })
        else:
            action.update({
                'view_mode': 'tree',
                'domain': [('id', 'in', self.purchase_request_related.ids)],
            })

        return action

    # def action_create_invoice(self):

    #     # Llamar al método original y obtener el resultado
    #     result = super(PurchaseOrder, self).action_create_invoice()

    #     _logger.warning(result['res_id'])
    #     invoice_id = result['res_id']

    #     # Obtener todos los nombres de las órdenes de compra seleccionadas y concatenarlos
    #     concatenated_names = ' '.join(self.mapped('name'))

    #     # Buscar las líneas contables asociadas a la factura
    #     aml = self.env['account.move.line'].search([
    #         ('move_id', '=', invoice_id),
    #         ('account_id.internal_type', '=', 'payable')
    #     ])

    #     # Asignar el texto concatenado al campo `name` de las líneas contables
    #     aml.write({'name': concatenated_names})

    #     return result