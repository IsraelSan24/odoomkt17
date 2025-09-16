from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"
    
    is_analytic_account_required = fields.Boolean(string='Centro de costo requerido')
    
    account_target_move_type = fields.Selection(
        string='Tipo entrada de destino en la cuenta',
        selection=[
            ('entry', 'Entradas de diario'),
            ('analytic', 'Cuenta analítica')
        ],
        default=None
    )
    debit_target_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cta. destino Debe'
    )
    credit_target_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Cta. detino Haber'
    )
