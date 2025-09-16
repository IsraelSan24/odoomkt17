from odoo import fields, models, api


# TODO: DELETE IN V17
class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'
    
    inverse_rate = fields.Float( 
        string='Tipo de cambio (Deprecado)',
        compute='_compute_inverse_rate', 
        compute_sudo=True,
        store=True,
        readonly=True,
        digits=(10,3)
    )
    
    @api.depends('date', 'statement_id.currency_id', 'statement_id.company_id', 'statement_id.company_id.currency_id')
    def _compute_inverse_rate(self):
        for order in self:
            order.inverse_rate= self.env['res.currency']._get_conversion_rate(order.statement_id.currency_id, order.statement_id.company_id.currency_id, order.statement_id.company_id, order.date)
