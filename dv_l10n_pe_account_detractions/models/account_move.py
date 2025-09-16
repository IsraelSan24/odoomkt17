from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_pe_is_subject_to_detraction = fields.Boolean(
        string='Sujeto a Detracción')
    l10n_pe_detraction_table_id = fields.Many2one(
        'l10n_pe_detraction.table', string='Codigo de detracción')
    l10n_pe_detraction_percent = fields.Float(
        string='Porcentaje de detracción', related='l10n_pe_detraction_table_id.percent', readonly=False)
    l10n_pe_proof_detraction_deposit_date = fields.Date(
        string='Fecha de emisión de la Constancia de Depósito de Detracción (5)')
    l10n_pe_proof_detraction_deposit_number = fields.Char(
        string='Número de la Constancia de Depósito de Detracción (5)')
    l10n_pe_detraction_amount = fields.Monetary(
        string='Monto de detracción', compute='_compute_detraction_amount')

    l10n_pe_has_detraction_line = fields.Boolean(
        string='Tiene apunte de detracción', compute='_compute_l10n_pe_has_detraction_line', store=True)

    @api.depends('line_ids')
    def _compute_l10n_pe_has_detraction_line(self):
        for record in self:
            l10n_pe_has_detraction_line = False
            for line in record.line_ids:
                if line.l10n_pe_is_detraction_line:
                    l10n_pe_has_detraction_line = True
            record.l10n_pe_has_detraction_line = l10n_pe_has_detraction_line

    @api.depends('l10n_pe_detraction_table_id', 'amount_total')
    def _compute_detraction_amount(self):
        for record in self:
            l10n_pe_detraction_amount = False
            if record.l10n_pe_detraction_percent:
                l10n_pe_detraction_amount = record.amount_total * \
                    record.l10n_pe_detraction_percent
            record.l10n_pe_detraction_amount = l10n_pe_detraction_amount

    def _post(self, soft=True):
        for move in self:
            if move.l10n_pe_is_subject_to_detraction and move.l10n_pe_detraction_table_id and not move.company_id.detraction_account_id:
                raise UserError(
                    'Debe asignar una cuenta contable de detracción.')
            if not move.invoice_date and move.move_type != 'entry':
                raise UserError(
                    'Debe asignar una fecha de emisión.')
            if move.l10n_pe_detraction_table_id and not move.l10n_pe_has_detraction_line:
                line_data = {
                    'name': 'Detracción',
                    'ref': move.name,
                    'partner_id': move.partner_id and move.partner_id.id or False,
                    'currency_id': move.currency_id and move.currency_id.id or False,
                    'l10n_pe_is_detraction_line': True,
                }
                debit_data = dict(line_data)
                credit_data = dict(line_data)

                if move.move_type in ('in_invoice', 'in_refund', 'in_receipt'):
                    debit_account_id = move.partner_id.property_account_payable_id.id
                    credit_account_id = move.company_id.detraction_account_id.id

                if move.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                    debit_account_id = move.company_id.detraction_account_id.id
                    credit_account_id = move.partner_id.property_account_receivable_id.id
                    
                debit_data.update(
                    account_id=debit_account_id,
                    debit=move.currency_id._convert(move.l10n_pe_detraction_amount, move.company_id.currency_id, move.company_id, move.invoice_date),
                    credit=False,
                    amount_currency = move.l10n_pe_detraction_amount
                )
                credit_data.update(
                    account_id=credit_account_id,
                    debit=False,
                    credit=move.currency_id._convert(move.l10n_pe_detraction_amount, move.company_id.currency_id, move.company_id, move.invoice_date),
                    amount_currency = -1 * move.l10n_pe_detraction_amount
                )
                
                move.line_ids = [(0, 0, debit_data), (0, 0, credit_data)]
        res = super(AccountMove, self)._post(soft=soft)
        return res
