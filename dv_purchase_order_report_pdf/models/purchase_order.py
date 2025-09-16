from odoo import fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    responsible_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsable'
    )
    # INDOMIN
    shipping_type = fields.Selection(
        string='Tipo de entrega',
        selection=[
            ('own_wh', 'Envio alm Indomin'),
            ('provider_wh', 'Recojo alm proveedor'),
        ],
        required=True,
        default='own_wh',
    )
