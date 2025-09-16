from odoo import api, fields, models


class ServiceOrderPart(models.Model):
    _name = 'service.order.part'
    _description = 'Piezas Requeridas de la Orden de Trabajo'

    service_order_id = fields.Many2one(
        string='Órden de trabajo',
        comodel_name='service.order',
        ondelete='cascade'
    )
    item = fields.Integer(
        string='Item',
        compute='_compute_item',
        store=True
    )
    control = fields.Char(string='Control')
    description = fields.Many2one(
        comodel_name='product.product',
        string='Descripción',
        domain=[('type', '!=', 'service')],
        help='Seleccione un producto como pieza requerida.'
    )
    part_number = fields.Char(string='Número de Parte')
    activity_task = fields.Char(string='Actividad')
    quantity = fields.Integer(
        string='Cantidad',
        default=1
    )
    area = fields.Char(string='Área')
    # Método para numerar automáticamente los ítems
    @api.depends('service_order_id.parts_required_ids')
    def _compute_item(self):
        for record in self:
            items = record.service_order_id.parts_required_ids
            for index, part in enumerate(items, start=1):
                part.item = index
