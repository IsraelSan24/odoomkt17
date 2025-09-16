from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_names = fields.Char(
        compute='_compute_analytic_names'
    )

    def _compute_analytic_names(self):
        for move in self:
            names = []

            for aid in move.analytic_distribution:
                analytic = self.env['account.analytic.account'].browse(int(aid))
                names.append(analytic)
            move.analytic_names = ', '.join(names)
