from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    to_force_exchange_rate = fields.Float(
        string='Forzar T.C.',
        digits=(12, 12),
        help='''Este campo se utiliza para forzar la tasa de cambio. Representa la tasa inversa, es decir, la cantidad de dólares necesarios para obtener 1 sol.
        Por ejemplo, si la tasa de cambio es 3.80, significa que 1 sol equivale a 3.80 dólares, y la tasa inversa sería 1 / 3.80 ≈ 0.2632.
        Este último valor se debería en este campo.
        ''',
        compute='_compute_to_force_exchange_rate',
        inverse='_inverse_exchange_rate'
    )
    exchange_rate = fields.Float(
        string='Tipo de Cambio',
        digits=0,
        store=True
    )
    @api.depends('exchange_rate')
    def _compute_to_force_exchange_rate(self):
        for payment in self:
            if payment.exchange_rate != 0.0 and payment.currency_id != payment.company_currency_id:
                payment.to_force_exchange_rate = 1 / payment.exchange_rate

    def _inverse_exchange_rate(self):
        for payment in self:
            if payment.to_force_exchange_rate != 0.0 and payment.currency_id != payment.company_currency_id:
                payment.exchange_rate = 1 / payment.to_force_exchange_rate

    @api.onchange('currency_id', 'company_id', 'to_force_exchange_rate')
    def _onchange_to_force_exchange_rate(self):
        if self.currency_id == self.company_currency_id:
            self.to_force_exchange_rate = 0.0
            self.exchange_rate = 0.0

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        line_vals_list = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals, force_balance)

        if self.currency_id and self.currency_id != self.company_currency_id and self.to_force_exchange_rate != 0.0:

            for line_vals in line_vals_list:
                liquidity_amount_currency = line_vals.get('amount_currency', 0.0)
                liquidity_balance = self.currency_id._force_convert(
                    liquidity_amount_currency,
                    self.company_id.currency_id,
                    self.company_id,
                    self.to_force_exchange_rate
                )
                line_vals.update({
                    'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                    'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                })

        return line_vals_list
