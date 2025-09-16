from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    debit_target_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cta. destino Debe'
    )
    credit_target_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cta. destino Haber'
    )
    