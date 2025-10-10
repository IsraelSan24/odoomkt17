from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'
    stock_picking_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="gre_account_move_id",
        string="Reference Guides"
    )