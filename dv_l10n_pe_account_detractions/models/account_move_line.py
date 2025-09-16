from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_pe_is_detraction_line = fields.Boolean(string='Es apunte de detracción')
