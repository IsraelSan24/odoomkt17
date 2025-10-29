# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    stock_picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        relation='account_move_stock_picking_m2m_rel',   # tabla M2M nueva para evitar conflictos
        column1='account_move_id',
        column2='stock_picking_id',
        string='Reference Guides',
        help='Selecciona guías de remisión existentes (con gre_doc_name).',
    )

    @api.onchange('stock_picking_ids')
    def _onchange_stock_picking_ids_sync_gre(self):
        """
        Si existe gre_account_move_id en stock.picking, sincroniza:
        - Asigna gre_account_move_id = self.id a las guías añadidas.
        - Limpia gre_account_move_id en las guías removidas (si estaban vinculadas a este move).
        """
        Picking = self.env['stock.picking']
        if 'gre_account_move_id' not in Picking._fields:
            return

        if not self._origin:
            # En new records, no hay delta fiable; hacer solo asignación al guardar o confiar en constraint
            return

        before = self._origin.stock_picking_ids
        after = self.stock_picking_ids

        removed = before - after
        added = after - before

        # Limpiar las removidas solo si estaban asociadas a este move
        if removed:
            removed.filtered(lambda p: p.gre_account_move_id == self._origin).write({'gre_account_move_id': False})
        # Asignar las nuevas
        if added:
            added.write({'gre_account_move_id': self.id})

    @api.constrains('stock_picking_ids')
    def _check_unique_linked_pickings(self):
        """
        Evita que una guía esté vinculada a otra factura distinta cuando se usa gre_account_move_id.
        (Doble seguridad además del dominio)
        """
        Picking = self.env['stock.picking']
        if 'gre_account_move_id' not in Picking._fields:
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