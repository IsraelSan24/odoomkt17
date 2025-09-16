from odoo import _, fields, models


class PartnerDeliveryAddress(models.Model):
    _name = 'partner.delivery.address'
    _description = 'Direcciones Personalizadas de Proveedores'

    name = fields.Char(
        string='Dirección',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor',
        required=True,
        ondelete='cascade'
    )
