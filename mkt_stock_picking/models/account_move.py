from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Reemplaza el One2many por Many2many para poder "elegir existentes"
    stock_picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        relation='account_move_stock_picking_rel',
        column1='move_id',
        column2='picking_id',
        string='Reference Guides',
        help='Selecciona guías de remisión existentes.'
    )

    @api.constrains('stock_picking_ids')
    def _check_unique_linked_pickings(self):
        """Evita que una guía esté vinculada a otra factura si así lo deseas."""
        for move in self:
            # si usas gre_account_move_id como vínculo exclusivo en picking:
            linked_elsewhere = move.stock_picking_ids.filtered(
                lambda p: p.gre_account_move_id and p.gre_account_move_id != move
            )
            if linked_elsewhere:
                names = ", ".join(linked_elsewhere.mapped('display_name'))
                raise ValidationError(_(
                    "Las siguientes guías ya están vinculadas a otro comprobante: %s", names
                ))