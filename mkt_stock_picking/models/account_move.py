# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Many2many para seleccionar guías existentes (sin crear/editar desde la factura)
    stock_picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        relation='account_move_stock_picking_m2m_rel',   # tabla M2M nueva para evitar conflictos
        column1='account_move_id',
        column2='stock_picking_id',
        string='Reference Guides',
        help='Selecciona guías de remisión existentes.',
    )

    @api.constrains('stock_picking_ids')
    def _check_unique_linked_pickings(self):
        """
        Si tu negocio exige exclusividad (una guía solo puede estar en una factura),
        valida contra gre_account_move_id cuando ese campo exista en stock.picking.
        """
        picking_has_field = 'gre_account_move_id' in self.env['stock.picking']._fields
        if not picking_has_field:
            return
        for move in self:
            linked_elsewhere = move.stock_picking_ids.filtered(
                lambda p: p.gre_account_move_id and p.gre_account_move_id != move
            )
            if linked_elsewhere:
                names = ", ".join(linked_elsewhere.mapped('display_name'))
                raise ValidationError(_(
                    "Las siguientes guías ya están vinculadas a otro comprobante: %s") % names
                )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Aseguramos que la búsqueda/visualización priorice gre_doc_name
    gre_doc_name = fields.Char()

    def name_get(self):
        res = []
        for p in self:
            # Prioriza gre_doc_name; de lo contrario usa el name del picking
            name = p.gre_doc_name or p.name or _("(Sin nombre)")
            res.append((p.id, name))
        return res
