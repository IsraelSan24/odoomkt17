from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    stock_move_id = fields.Many2one(
        string='Id movimiento',
        comodel_name='stock.move',
        ondelete='cascade'
    )
