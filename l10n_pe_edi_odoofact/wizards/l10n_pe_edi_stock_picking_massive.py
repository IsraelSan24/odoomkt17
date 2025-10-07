from odoo import models, fields, api

class L10nPeEdiStockPickingMassiveWizard(models.TransientModel):
    _name = 'l10n.pe.edi.stock.picking.massive'
    _description = 'Stock Picking Massive Wizard'

    invoice_id = fields.Many2one('account.move', string='Invoice', required=True)
    picking_ids = fields.Many2many('stock.picking', string='Referral Guides')

    def action_add_picking(self):
        picking_number_values = []
        for line in self.picking_ids:
            picking_number_values.append({
                'type': '1',
                'name': line.l10n_pe_edi_picking_name,
            })
        if picking_number_values:
            self.invoice_id.write({
                'l10n_pe_edi_picking_number_ids': [(0, 0, vals) for vals in picking_number_values]
            })